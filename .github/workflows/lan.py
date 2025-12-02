#!/usr/bin/env python3
import boto3
import sys
import json
import time
import socket

# =============================================================
# JMeter EC2 Instance Starter with SSH Validation and Fallback
# -------------------------------------------------------------
# - Selects 1 master + N slaves from stopped pool
# - Starts them and waits until running
# - Verifies SSH reachability (port 22)
# - If unreachable → stops and replaces with another
# - Writes instance_info.json (for pipeline)
# - Writes summary.json (for logs and debugging)
# =============================================================

REGION = "us-east-1"
ec2 = boto3.client("ec2", region_name=REGION)

master_list = [
    "awslsdjmetermasterapp01",
    "awslsdjmetermasterapp02",
    "awslsdjmetermasterapp03",
    "awslsdjmetermasterapp04",
]

slave_list = [
    "awslsdjmeterslaveapp01",
    "awslsdjmeterslaveapp02",
    "awslsdjmeterslaveapp03",
    "awslsdjmeterslaveapp04",
    "awslsdjmeterslaveapp05",
    "awslsdjmeterslaveapp06",
    "awslsdjmeterslaveapp07",
    "awslsdjmeterslaveapp08",
    "awslsdjmeterslaveapp09",
    "awslsdjmeterslaveapp10",
    "awslsdjmeterslaveapp11",
    "awslsdjmeterslaveapp12",
    "awslsdjmeterslaveapp13",
    "awslsdjmeterslaveapp14",
    "awslsdjmeterslaveapp15",
]

# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def describe_instances_by_name(names, state_filter=None):
    filters = [{"Name": "tag:Name", "Values": names}]
    if state_filter:
        filters.append({"Name": "instance-state-name", "Values": [state_filter]})
    try:
        response = ec2.describe_instances(Filters=filters)
        instances = []
        for r in response["Reservations"]:
            for inst in r["Instances"]:
                name = next(
                    (tag["Value"] for tag in inst.get("Tags", []) if tag["Key"] == "Name"),
                    "",
                )
                instances.append(
                    {
                        "id": inst["InstanceId"],
                        "name": name,
                        "ip": inst.get("PrivateIpAddress", ""),
                        "role": "master" if "master" in name.lower() else "slave",
                    }
                )
        return instances
    except Exception as e:
        print(f"[ERROR] describe_instances failed: {e}")
        return []


def is_ssh_ready(ip, timeout=300):
    """Check SSH port 22 availability with timeout (max 5 min)."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((ip, 22), timeout=5):
                print(f"[INFO] SSH reachable for {ip}")
                return True
        except (socket.timeout, OSError):
            time.sleep(10)
    print(f"[WARN] SSH unreachable for {ip} after {timeout} seconds")
    return False


def start_instances(instance_ids):
    try:
        ec2.start_instances(InstanceIds=instance_ids)
        print(f"[INFO] Starting instances: {instance_ids}")
        waiter = ec2.get_waiter("instance_running")
        waiter.wait(InstanceIds=instance_ids)
        print(f"[INFO] All instances are now running")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to start instances: {e}")
        return False


def stop_instance(instance_id, reason="Manual stop due to SSH failure"):
    try:
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"[WARN] Stopped instance {instance_id}: {reason}")
    except Exception as e:
        print(f"[ERROR] Failed to stop instance {instance_id}: {e}")


# -------------------------------------------------------------
# Main Start Logic
# -------------------------------------------------------------
def start_and_validate(slave_count):
    summary = {"started": [], "failed": [], "replaced": []}

    # 1️⃣ Select stopped master and N stopped slaves
    stopped_masters = describe_instances_by_name(master_list, "stopped")
    stopped_slaves = describe_instances_by_name(slave_list, "stopped")

    if not stopped_masters:
        print("[ERROR] No stopped master instances found.")
        sys.exit(1)

    selected_master = stopped_masters[0]
    selected_slaves = stopped_slaves[:slave_count]

    if len(selected_slaves) < slave_count:
        print("[ERROR] Not enough stopped slave instances available.")
        sys.exit(1)

    all_selected = [selected_master] + selected_slaves
    instance_ids = [i["id"] for i in all_selected]

    print(f"[INFO] Starting master: {selected_master['name']}")
    print(f"[INFO] Starting slaves: {[s['name'] for s in selected_slaves]}")

    # 2️⃣ Start and wait until running
    if not start_instances(instance_ids):
        sys.exit(1)

    # 3️⃣ Re-fetch running info (with IPs)
    running_instances = describe_instances_by_name(
        [i["name"] for i in all_selected], "running"
    )

    # 4️⃣ SSH health check + fallback replacement
    for inst in running_instances:
        ip = inst.get("ip")
        if not ip or not is_ssh_ready(ip):
            summary["failed"].append(inst["name"])
            stop_instance(inst["id"], "SSH not reachable")

            # Try to replace from remaining stopped pool
            pool = (
                stopped_masters[1:]
                if inst["role"] == "master"
                else stopped_slaves[slave_count:]
            )
            if pool:
                new = pool[0]
                print(f"[INFO] Replacing {inst['name']} with {new['name']}")
                if start_instances([new["id"]]):
                    new_ip = describe_instances_by_name([new["name"]], "running")[0][
                        "ip"
                    ]
                    if is_ssh_ready(new_ip):
                        inst.update(new)
                        inst["ip"] = new_ip
                        summary["replaced"].append(
                            {"old": inst["name"], "new": new["name"]}
                        )
                        continue
            print(f"[CRITICAL] Could not replace {inst['name']}")
        else:
            summary["started"].append(inst["name"])

    # 5️⃣ Write output files
    with open("instance_info.json", "w") as f:
        json.dump(running_instances, f, indent=4)
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    print("[INFO] instance_info.json and summary.json written successfully")
    print(json.dumps(summary, indent=2))


# -------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python start_instance.py <slave_count>")
        sys.exit(1)

    try:
        slave_count = int(sys.argv[1])
        start_and_validate(slave_count)
    except ValueError:
        print("[ERROR] Invalid slave count.")
        sys.exit(1)
