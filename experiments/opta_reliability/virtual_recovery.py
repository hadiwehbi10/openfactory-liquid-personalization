"""Isolated OPC UA reconnect experiment; never accesses the physical OPTA.

Run inside the opcua-gateway Docker image with ``--network none``.
This tests a clean server shutdown and restart, not a cable-pull failure.
"""

import asyncio
import time

from asyncua import Client, Server, ua


ENDPOINT = "opc.tcp://127.0.0.1:48401/virtual-test/"
NAMESPACE = "urn:openfactory:virtual-recovery-test"


class ChangeHandler:
    def __init__(self):
        self.values = []

    def datachange_notification(self, node, value, data):
        self.values.append(value)
        print(f"DATA CHANGE: {value}", flush=True)


async def make_server():
    server = Server()
    await server.init()
    server.set_endpoint(ENDPOINT)
    ns = await server.register_namespace(NAMESPACE)
    station = await server.nodes.objects.add_object(
        ua.NodeId("VirtualStation", ns), "VirtualStation"
    )
    heartbeat = await station.add_variable(
        ua.NodeId("Heartbeat", ns), "Heartbeat", 0
    )
    await heartbeat.set_writable()
    await server.start()
    return server, heartbeat, ns


async def run_experiment():
    print("TEST: virtual OPC UA server restart and subscription recovery", flush=True)
    print(f"ENDPOINT: {ENDPOINT} (container loopback only)", flush=True)
    server, heartbeat, ns = await make_server()
    client = Client(ENDPOINT, timeout=3)
    handler = ChangeHandler()
    loss_times = []

    async def on_connection_lost(exc):
        loss_times.append(time.monotonic())
        print(f"CONNECTION LOST: {exc}", flush=True)

    client.connection_lost_callback = on_connection_lost
    restarted_server = None
    try:
        await client.connect(auto_reconnect=True, reconnect_max_delay=1.0)
        node = client.get_node(ua.NodeId("Heartbeat", ns))
        subscription = await client.create_subscription(100, handler)
        await subscription.subscribe_data_change(node)
        print("SUBSCRIPTION: monitored heartbeat variable", flush=True)
        await heartbeat.write_value(1)
        for _ in range(30):
            if 1 in handler.values:
                break
            await asyncio.sleep(0.1)
        if 1 not in handler.values:
            raise RuntimeError("Initial subscription did not receive heartbeat=1")
        print("BASELINE: subscription received heartbeat=1", flush=True)

        print("EVENT: stopping virtual OPC UA server", flush=True)
        await server.stop()
        server = None
        await asyncio.sleep(2)
        print(f"LOSS CALLBACK OBSERVED: {bool(loss_times)}", flush=True)

        print("EVENT: restarting virtual OPC UA server", flush=True)
        restarted_server, new_heartbeat, new_ns = await make_server()
        if new_ns != ns:
            raise RuntimeError("Namespace ID changed across server restart")
        restart_at = time.monotonic()

        # Repeatedly update the new server-side value, so an automatically
        # restored subscription has an opportunity to report a fresh change.
        recovered = False
        for i in range(40):
            await new_heartbeat.write_value(100 + i)
            await asyncio.sleep(0.5)
            if any(type(v) is int and v >= 100 for v in handler.values):
                recovered = True
                break

        if not recovered:
            print("RESULT: FAIL (no post-restart subscription event within 20 s)", flush=True)
            return 1

        print(f"RESULT: PASS (subscription recovered in {time.monotonic() - restart_at:.2f} s)", flush=True)
        print("NOTE: This tests a virtual server restart, not the OPTA's HEL/ACK failure.", flush=True)
        return 0
    finally:
        try:
            await asyncio.wait_for(client.disconnect(), timeout=5)
        except Exception as exc:
            print(f"CLEANUP: client disconnect warning: {exc}", flush=True)
        for active_server in (restarted_server, server):
            if active_server is not None:
                try:
                    await asyncio.wait_for(active_server.stop(), timeout=5)
                except Exception as exc:
                    print(f"CLEANUP: server stop warning: {exc}", flush=True)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_experiment()))
