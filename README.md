
# Bluetooth BMS Reader for Ultimatron / JBD LiFePO₄ Batteries

python script in rasbery pi connects to the BMS over BLE, decodes key battery parameters (voltage, current, capacity, cell voltages, cycles, etc.), and publishes the data to an **MQTT broker**.  
It also saves the data locally in **JSONL format** for logging or further analysis.

---

## Features

- Connects to BLE BMS using [`bluepy`](https://ianharvey.github.io/bluepy-doc/)
- Retrieves:
  - Total battery voltage, current, power, and remaining capacity
  - Per-cell voltages
  - Cycle count
- Publishes all readings to an MQTT topic (e.g., `batterie/myBattery`)
- Logs each reading as a line in `bms_data.jsonl`
- 
---

## How It Works

The script communicates with the BMS using the **JBD protocol**, a common serial/BLE protocol used by many smart BMS devices.

Two key BLE commands are used:

| Command      | Hex Value                    | Purpose                                                                      |
|--------------|------------------------------|------------------------------------------------------------------------------|
| `CMD_INFO`   | `DD A5 03 00 FF FD 77`       | Requests basic battery information (voltage, current, capacity, cycles, etc.) |
| `CMD_VCELL`  | `DD A5 04 00 FF FC 77`       | Requests individual cell voltages |

Each command is sent via BLE characteristic `0x15`, and the BMS responds with binary data packets.  
The script decodes these packets using Python’s `struct` module.

## Command Structure

**General Format:**


[START_BYTE][COMMAND][REGISTER][DATA_LENGTH][CRC_CHECKSUM][END_BYTE]



Each field in the frame has a defined meaning:

| Field  | Description |
|--------|-------------|
| `START_BYTE` | Always `0xDD` — marks the beginning of the command frame |
| `COMMAND` | Command type (e.g., `0xA5` for read, `0x5A` for write) |
| `REGISTER` | Specifies what data to read/write (e.g., info, voltage, temperature) |
| `DATA_LENGTH` | Number of data bytes following (often `0x00` for read requests) |
| `CRC_CHECKSUM` | 2-byte checksum for command validation |
| `END_BYTE` | Always `0x77` — marks the end of the frame |



### CMD_INFO — Basic Battery Information
**Hex Command:**
CMD_INFO = b'\xdd\xa5\x03\x00\xff\xfd\x77
| Byte Position | Hex Value  | Decimal | Description                      |
| ------------- | ---------- | ------- | -------------------------------- |
| 0             | `\xdd`     | 221     | Start Byte — command frame start |
| 1             | `\xa5`     | 165     | Command Type — read operation    |
| 2             | `\x03`     | 3       | Register — basic info register   |
| 3             | `\x00`     | 0       | Data Length — no payload         |
| 4–5           | `\xff\xfd` | 65533   | CRC Checksum — validates frame   |
| 6             | `\x77`     | 119     | End Byte — command frame end     |


## CMD_VCELL — Cell Voltage Information
**Hex Command:**
CMD_VCELL = b'\xdd\xa5\x04\x00\xff\xfc\x77'

| Byte Position | Hex Value  | Decimal | Description                       |
| ------------- | ---------- | ------- | --------------------------------- |
| 0             | `\xdd`     | 221     | Start Byte — command frame start  |
| 1             | `\xa5`     | 165     | Command Type — read operation     |
| 2             | `\x04`     | 4       | Register — cell voltages register |
| 3             | `\x00`     | 0       | Data Length — no payload          |
| 4–5           | `\xff\xfc` | 65532   | CRC Checksum — validates frame    |
| 6             | `\x77`     | 119     | End Byte — command frame end      |


## Register Map


| Register      | Hex    | Decimal | Description                        |
| ------------- | ------ | ------- | ---------------------------------- |
| Basic Info    | `0x03` | 3       | Voltage, current, capacity, cycles |
| Cell Voltages | `0x04` | 4       | Per-cell voltage values            |
| Temperature   | `0x05` | 5       | Temperature sensor readings        |
| Protection    | `0x06` | 6       | Protection and error status flags  |

Responses are binary-encoded and must be decoded using struct.unpack() according to the BMS data format.



Staying connected for long periods is was causing unstability to the system so .
I connect → read → disconnect → sleep.

## References

GitHub: tgalarneau/bms – jbdbms-4-socket-2temps.py

Smart BMS Protocol documentation (JBD / Xiaoxiang / Ultimatron-compatible)

https://github.com/tgalarneau/bms/tree/main

https://endless-sphere.com/forums/viewtopic.php?t=91672

https://github.com/tgalarneau/bms

https://github.com/Jakeler/Jakeler.github.io/issues/16


---------




=======
# bleak_and_Paho



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.ei.htwg-konstanz.de/mpsys/ws2526/bleak_and_paho.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://gitlab.ei.htwg-konstanz.de/mpsys/ws2526/bleak_and_paho/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
* [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)


