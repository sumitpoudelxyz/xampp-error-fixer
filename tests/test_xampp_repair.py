import importlib.util
from pathlib import Path
from unittest.mock import patch
import subprocess

SCRIPT = Path(__file__).resolve().parents[1] / "Repair Scripts" / "xampp_repair.py"
spec = importlib.util.spec_from_file_location("xampp_repair", SCRIPT)
repair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repair)


def test_fix_mysql_refuses_to_modify_database_files(tmp_path):
    data_dir = tmp_path / "mysql" / "data"
    data_dir.mkdir(parents=True)
    important = data_dir / "keep-me.sql"
    important.write_text("valuable database content", encoding="utf-8")

    assert repair.fix_mysql(str(tmp_path)) is False
    assert important.read_text(encoding="utf-8") == "valuable database content"


def test_backup_file_creates_timestamped_copy(tmp_path):
    config = tmp_path / "httpd.conf"
    config.write_text("Listen 80\n", encoding="utf-8")

    backup = Path(repair.backup_file(str(config)))

    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "Listen 80\n"
    assert backup != config


def test_get_port_usage_matches_exact_port_not_prefix():
    netstat = subprocess.CompletedProcess(
        args=["netstat", "-ano"],
        returncode=0,
        stdout="  TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING    1234\n",
        stderr="",
    )
    with patch.object(repair.subprocess, "run", return_value=netstat):
        assert repair.get_port_usage(80) is None


def test_get_port_usage_returns_matching_listener():
    netstat = subprocess.CompletedProcess(
        args=["netstat", "-ano"],
        returncode=0,
        stdout="  TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING    1234\n",
        stderr="",
    )
    tasklist = subprocess.CompletedProcess(
        args=["tasklist"],
        returncode=0,
        stdout="Image Name                     PID\nhttpd.exe                     1234\n",
        stderr="",
    )
    with patch.object(repair.subprocess, "run", side_effect=[netstat, tasklist]):
        assert repair.get_port_usage(8080) == {"process": "httpd.exe", "pid": "1234"}
