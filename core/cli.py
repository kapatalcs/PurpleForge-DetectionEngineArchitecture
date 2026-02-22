import threading
import subprocess
import time
import sys
from pathlib import Path
import psutil
import json

from core.config_loader import ConfigLoader
from parsers.mainparser import main_parser
from detector.engine import PurpleForgeDetectionEngine
from detector.rules import RULE_CLASSES
from core.lab_registry import add_lab, remove_lab, get_active_labs

ATTACKS = ["password_spray","distributed_password_spray","credential_stuffing_attack","distributed_credential_stuffing_attack",
           "double_extension",
           "mime_spoofing",
           "server_side_request_forgery",
           "insecure_direct_object_reference","missing_function_level_access_control","server_side_template_injection",
           "json_web_token_none_algorithm"]

alert_received = threading.Event()

def show_attack_menu(attacks):
    print("\n=== PurpleForge ===")
    print("Please select an attack scenario:\n")

    for idx, attack in enumerate(attacks, start=1):
        print(f"{idx}. {attack}")

    while True:
        try:
            choice = input("\nSelection (number): ").strip()

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            choice = int(choice)
            if 1 <= choice <= len(attacks):
                return attacks[choice - 1]

            print("Invalid selection.")

        except KeyboardInterrupt:
            print("\nExiting...")
            raise SystemExit



def is_process_alive(pid: int) -> bool:
    return psutil.pid_exists(pid)


def start_lab(lab_name: str):
    lab_dir = Path("labs") / lab_name
    lab_path = lab_dir / "app.py"
    pid_file = lab_dir / "lab.pid"

    if not lab_path.exists():
        raise FileNotFoundError(f"Lab not found: {lab_path}")

    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        if is_process_alive(pid):
            print(f"Lab '{lab_name}' already working (PID={pid})")
            add_lab(lab_name)
            return None
        else:
            pid_file.unlink()

    process = subprocess.Popen(
        [sys.executable, str(lab_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    pid_file.write_text(str(process.pid))
    print(f"Lab '{lab_name}' has been started. (PID={process.pid})")
    add_lab(lab_name)
    return process


def stop_lab(lab_name: str):
    pid_file = Path("labs") / lab_name / "lab.pid"
    if not pid_file.exists():
        return

    pid = int(pid_file.read_text().strip())

    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=5)
        print(f"Lab closed (PID={pid})")
    except psutil.TimeoutExpired:
        p.kill()
    except psutil.NoSuchProcess:
        pass
    finally:
        remove_lab(lab_name)
        pid_file.unlink(missing_ok=True)    


def run_attack(attack_name: str) -> bool:
    attack_path = Path("simulations") / attack_name / "simulate.py"

    if not attack_path.exists():
        print(f"[CLI] Attack not found: {attack_path}")
        return False

    result = subprocess.run(
        [sys.executable, str(attack_path)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return True

    return False


def load_rules():
    return [rule_cls() for rule_cls in RULE_CLASSES.values()]


def engine_loop(engine: PurpleForgeDetectionEngine):
    print("Detection Engine started")

    while True:
        for lab_name in get_active_labs():
            try:
                events = main_parser(lab_name)
            except Exception as e:
                print(f"[ENGINE ERROR] parser failed for {lab_name}: {e}")
            for event in events:
                alerts = engine.process(event) or []
                for alert in alerts:
                    print("🚨 ALERT:", json.dumps(alert, indent=4,ensure_ascii=False))
                    alert_received.set()

        time.sleep(1)

def attack_listener(attacks: list):
    alert_received.wait()
    
    while True:
        cmd = input("\n[a] Run Attack | [q] Exit: ").strip().lower()

        if cmd == "a":
            alert_received.clear()
            attack, lab = select_attack_scenario(attacks)
            if attack:
                execute_attack_flow(attack, lab)
                alert_received.wait()

        elif cmd == "q":
            print("Exiting...")
            break

def select_attack_scenario(attacks):
    selected_attack = show_attack_menu(attacks)

    loader = ConfigLoader()
    attack_info = loader.get_attack_config(selected_attack)

    if not attack_info:
        print("Attack config not found.")
        return None, None
        
    return selected_attack, attack_info["lab"]
    
def execute_attack_flow(attack_name, lab_name):
    started = start_lab(lab_name)
    if started is not None:
        time.sleep(2)

    run_attack(attack_name)

def main():
    selected_attack, lab_name = select_attack_scenario(ATTACKS)
    if not selected_attack:
        return

    engine = PurpleForgeDetectionEngine(rules=load_rules())

    threading.Thread(
        target=engine_loop,
        args=(engine,),
        daemon=True
    ).start()

    execute_attack_flow(selected_attack, lab_name)

    try:
        attack_listener(ATTACKS)
    finally:
        for lab in get_active_labs():
            stop_lab(lab)


if __name__ == "__main__":
    main()