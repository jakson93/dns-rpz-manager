import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.dns_server import DNSServer
from app.models.log import Log


class BindService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_zone(self, zone_name: Optional[str] = None, zone_file: Optional[str] = None) -> dict:
        zone_name = zone_name or settings.RPZ_ZONE_NAME
        zone_file = zone_file or settings.BIND_RPZ_PATH
        checkzone_path = settings.BIND_CHECKZONE_PATH

        try:
            process = await asyncio.create_subprocess_exec(
                checkzone_path, zone_name, zone_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
                "return_code": process.returncode,
            }
        except FileNotFoundError:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Checkzone not found at {checkzone_path}",
                "return_code": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
            }

    async def reload_dns(self, server_id: Optional[int] = None) -> list:
        results = []

        if server_id:
            result = await self.db.execute(select(DNSServer).where(DNSServer.id == server_id))
            server = result.scalar_one_or_none()
            if not server:
                return [{"server_id": server_id, "success": False, "error": "Server not found"}]
            servers = [server]
        else:
            result = await self.db.execute(
                select(DNSServer).where(DNSServer.is_active == True)
            )
            servers = result.scalars().all()

        for server in servers:
            try:
                rndc_path = settings.RNDC_PATH
                process = await asyncio.create_subprocess_exec(
                    rndc_path, "-s", server.hostname, "-p", str(server.port), "reload",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()

                server_result = {
                    "server_id": server.id,
                    "server_name": server.name,
                    "success": process.returncode == 0,
                    "stdout": stdout.decode("utf-8"),
                    "stderr": stderr.decode("utf-8"),
                }

                if process.returncode == 0:
                    server.last_sync = datetime.utcnow()
                    await self.db.flush()

                results.append(server_result)
            except FileNotFoundError:
                results.append({
                    "server_id": server.id,
                    "server_name": server.name,
                    "success": False,
                    "error": f"RNDC not found at {rndc_path}",
                })
            except Exception as e:
                results.append({
                    "server_id": server.id,
                    "server_name": server.name,
                    "success": False,
                    "error": str(e),
                })

        if results:
            log_entry = Log(
                event="dns_reload",
                description=f"Reloaded DNS on {len(results)} server(s)",
                details={"results": results},
            )
            self.db.add(log_entry)
            await self.db.flush()

        return results

    async def get_dns_status(self) -> list:
        result = await self.db.execute(
            select(DNSServer).where(DNSServer.is_active == True)
        )
        servers = result.scalars().all()

        status_list = []
        for server in servers:
            try:
                process = await asyncio.create_subprocess_exec(
                    settings.RNDC_PATH, "-s", server.hostname, "-p", str(server.port), "status",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                status_list.append({
                    "id": server.id,
                    "name": server.name,
                    "hostname": server.hostname,
                    "port": server.port,
                    "is_running": process.returncode == 0,
                    "last_sync": server.last_sync.isoformat() if server.last_sync else None,
                })
            except Exception:
                status_list.append({
                    "id": server.id,
                    "name": server.name,
                    "hostname": server.hostname,
                    "port": server.port,
                    "is_running": False,
                    "last_sync": server.last_sync.isoformat() if server.last_sync else None,
                })

        return status_list
