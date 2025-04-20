# DirTraveler

**DirTraveler** is a Python-based, multi-threaded web directory enumeration tool designed to uncover hidden directories and files on web servers. It supports recursive scanning, duplicate-content detection, customizable HTTP status codes, and real-time progress reporting.

## Features

- **Multi-threaded scanning** for high performance and speed.
- **Recursive traversal** up to a configurable depth to dive deep into web structures.
- **Duplicate-content detection** to skip redundant scans and conserve resources.
- **Customizable HTTP status codes** to define what constitutes a successful find.
- **Real-time progress output** showing queue size and visited URL count.

## Requirements

- Python 3.6 or higher
- `requests` library
- `termcolor` library

Install dependencies via pip:

```bash
pip install requests termcolor
```

## Installation

1. Clone the repository:
   ```bash
git clone https://github.com/yourusername/DirTraveler.git
cd DirTraveler
```
2. Ensure dependencies are installed (see Requirements).

## Usage

```bash
python Dirtraveler.py -u <target_url> -w <wordlist_file> [options]
```

### Options

| Flag                          | Description                                                                      |
|-------------------------------|----------------------------------------------------------------------------------|
| `-u, --url`                   | Target URL to scan (e.g., `http://example.com`) **(required)**                    |
| `-w, --wordlist`              | Path to wordlist file (one entry per line) **(required)**                        |
| `-r, --recursive`             | Enable recursive enumeration of discovered directories                            |
| `-c, --codes`                 | HTTP status codes to treat as valid finds (default: `200`–`399`)                 |
| `-d, --depth`                 | Maximum recursion depth (default: `3`)                                            |
| `-t, --threads`               | Number of concurrent threads to use (default: `10`)                               |
| `--detect-duplicates`         | Enable duplicate-content detection (default behavior)                             |
| `--no-detect-duplicates`      | Disable duplicate-content detection                                              |

## Examples

- **Basic scan**:
  ```bash
  python Dirtraveler.py -u https://example.com -w common.txt
  ```

- **Recursive scan with custom codes and depth**:
  ```bash
  python Dirtraveler.py -u https://example.com -w common.txt -r -c 200 301 302 -d 2
  ```

- **High-thread scan**:
  ```bash
  python Dirtraveler.py -u https://example.com -w common.txt -t 20
  ```


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

