# WiFi Router Performance Evaluator

Tool developed in Python to evaluate the performance and correct functioning of home Wi-Fi routers.  
It performs a full set of technical tests including speed, latency, jitter, packet loss, signal strength, Ethernet capacity, Wi-Fi capacity, automatic Wi-Fi connection, and full database logging of results.

---

## 📌 Introduction

This program allows the user to evaluate the performance of a router through a series of automated technical tests. It analyzes key parameters that directly affect connectivity quality in both wired and wireless networks.

The program evaluates:

- **Download and upload speed**
- **Latency, jitter, and packet loss** to internal and external servers
- **Ethernet port capacity testing**
- **Wi-Fi signal strength (RSSI)** on 2.4 GHz and 5 GHz (Wi-Fi 6 / Wi-Fi 5)
- **Wireless capacity via iperf3**

It also stores results in a **MySQL database**, allowing long-term analysis and verification.

---

## 📦 Requirements

### ✅ Software Required

- **Python 3**
- **iperf3** installed on the system

### 📚 Required Python Libraries

Install all dependencies using:

```bash
pip install pywifi speedtest-cli mysql-connector ping3 plumbum termcolor
```
## Libraries used:

- **pywifi** – Wi-Fi network scanning and management  
- **speedtest-cli** – Internet speed measurement  
- **mysql.connector** – Database logging  
- **ping3** – Latency, packet loss and jitter  
- **plumbum** – Command execution  
- **termcolor** – Colored terminal output  
- **Standard libraries:** time, json, logging  

---

## 🖥️ Hardware Required

- A router to be tested  
- A device (PC/laptop) with:  
  - Ethernet 1 Gbps port  
  - Wi-Fi 6 support  
  - An iperf3 server in the same network  
  - Running on a VM or a physical device  

---

## 🔐 Additional permissions

- Administrator/root privileges may be required  
- Ensure firewall rules allow ping and iperf3 traffic  
- Router must be correctly configured to accept tests  

---

## ⚙️ How the Program Works

### 1. Internet speed test  
**Function:** `test_internet_speed`  
Measures download and upload performance using speedtest.

### 2. Wi-Fi signal strength (RSSI)  
**Function:** `get_RSSI`  
Scans Wi-Fi networks multiple times and filters the router’s networks.

### 3. Latency, packet loss and jitter  
**Function:** `latencia`  
Pings the following servers:  
- Internal: **66.231.74.241**  
- External: **8.8.8.8**, **1.1.1.1**

### 4. Capacity testing (Ethernet & Wi-Fi)  
**Function:** `run_iperf3_client`  
Requires a running iperf3 server on the same network.

### 5. Automatic Wi-Fi connection  
**Function:** `connect_wifi`

### 6. Results presentation  
**Function:** `present_results`  
Computes average, max and min of RSSI, latency and jitter.

### 7. Requirement verification  
**Function:** `umbrales`  
Checks if results meet acceptable thresholds.  
Controls database commit behavior.

### 8. Database storage  
**Function:** `commit_base`  
Saves results into two MySQL tables:  
- Threshold compliance  
- Measured values  

---

## ▶️ How to Run the Program

Navigate to the directory and execute:

```bash
python3 test_router.py
```

## 🛠️ Important Variables to Configure

| Variable        | Description |
|-----------------|-------------|
| `network_password` | Wi-Fi password (same for all router SSIDs) |
| `redes` | List of Wi-Fi SSIDs of the router |
| `pruebas_wifi` | Number of Wi-Fi test scenarios (default: 3) |
| `n_muestras` | Number of RSSI samples per SSID (ideal: 30, min: 15) |
| `tiempo_ping` | Duration of ping tests (ideal: 600s, min: 300s) |
| `server_ip` | IP of iperf3 server |
| `tiempo_iperf1` | Duration of Ethernet capacity tests (ideal: 60s, min: 30s) |
| `ethernetip` | Local Ethernet interface IP |
| `tiempo_iperf2` | Duration of Wi-Fi capacity tests (ideal: 300s, min: 120s) |
| `wifiip` | Local Wi-Fi interface IP |

---

## 🗄️ Database Notes

`commit_base` must be configured according to:

- Database name  
- Table names  
- Credentials  
- Host  

Data is stored locally.

---

## 📘 File Structure

- `test_router.py`  
- `README.md`


