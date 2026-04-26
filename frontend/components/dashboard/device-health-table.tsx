import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableHeaderRow,
  TableRow,
} from "@/components/ui/table";
import type { Device } from "@/types/api";

export function DeviceHealthTable({ devices }: { devices: Device[] }) {
  return (
    <Card>
      <div className="mb-5">
        <CardTitle>Device Health</CardTitle>
        <CardDescription>Heartbeat freshness, firmware, and signal quality for each retrofitted controller.</CardDescription>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHead>
            <TableHeaderRow>
              <TableHeader>Device</TableHeader>
              <TableHeader>Pump</TableHeader>
              <TableHeader>Status</TableHeader>
              <TableHeader>Firmware</TableHeader>
              <TableHeader>RSSI</TableHeader>
              <TableHeader>Voltage</TableHeader>
            </TableHeaderRow>
          </TableHead>
          <TableBody>
            {devices.map((device) => (
              <TableRow key={device.id}>
                <TableCell>{device.id}</TableCell>
                <TableCell>{device.pump_id}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      device.status === "online"
                        ? "success"
                        : device.status === "degraded"
                          ? "warning"
                          : "danger"
                    }
                  >
                    {device.status}
                  </Badge>
                </TableCell>
                <TableCell>{device.firmware_version}</TableCell>
                <TableCell>{device.rssi ?? "N/A"} dBm</TableCell>
                <TableCell>{device.voltage ?? "N/A"} V</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}

