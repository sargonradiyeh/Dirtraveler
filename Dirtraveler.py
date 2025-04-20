#!/usr/bin/python
'''
Description: DirTraveler is a web directory enumeration tool for discovering hidden directories and files.

Requirements:
You need to install requests and termcolor (pip install requests termcolor)

Usage:
python Dirtraveler.py -u http://example.com -w wordlist.txt [-r] [-c 200 301 403] [-d 2] [-t 15]

Options:
  -u, --url       Target URL to scan
  -w, --wordlist  Wordlist file containing directories/files to check
  -r, --recursive Enable recursive scanning of discovered directories
  -c, --codes     HTTP status codes to consider as "found" (default: 200-399)
  -d, --depth     Maximum recursive depth (default: 3)
  -t, --threads   Number of concurrent threads (default: 10)

Notes:
- Efficiently discovers hidden web content using multi-threading
- Detects duplicate content to avoid redundant scanning
- Shows real-time progress during scanning
- Automatically manages resource usage with work queue

'''
import argparse 
import requests
import threading
from termcolor import cprint
import time
import queue
import hashlib

cprint(
    r"""
    
██████╗ ██╗██████╗ ████████╗██████╗  █████╗ ██╗   ██╗██╗     ███████╗██████╗ 
██╔══██╗██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██║   ██║██║     ██╔════╝██╔══██╗
██║  ██║██║██████╔╝   ██║   ██████╔╝███████║██║   ██║██║     █████╗  ██████╔╝
██║  ██║██║██╔══██╗   ██║   ██╔══██╗██╔══██║╚██╗ ██╔╝██║     ██╔══╝  ██╔══██╗
██████╔╝██║██║  ██║   ██║   ██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗██║  ██║
╚═════╝ ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝""", color = 'white')
cprint(
    r"""                                                                          
 ____ ____ _________ ____ ____ ____ ____ ____ ____ ____ 
||b |||y |||       |||S |||a |||r |||j |||o |||u |||n ||
||__|||__|||_______|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|

""", color = 'light_cyan')
MAX_WORKERS = 10  #Default value, will be updated from args if needed
MAX_RECURSIVE_DEPTH = 1 #Default value, will be updated from args if needed
visited = set()
visited_lock = threading.Lock()
work_queue = queue.Queue()  #Work queue to control task processing
active_count = 0  #Track active worker count
active_count_lock = threading.Lock()  #Lock for updating active count
content_hashes = {} #Global variables for content tracking (to avoid recursing into duplicates)
content_hash_lock = threading.Lock()

def worker(): #Worker function that's necessary for processing URLs from the queue
    global active_count
    while True:
        try:
            task = work_queue.get(timeout=1) #Get the next task with timeout to allow checking for program exit
            if task is None:  #None is the signal to exit it
                work_queue.task_done()
                break
                
            link, wordlist, recursive, valid_codes, current_depth = task
            dir_requester(link, wordlist, recursive, valid_codes, current_depth)
            work_queue.task_done()
        except queue.Empty:
            continue #Queue empty for now, just continue... no problem
        except Exception as e:
            if work_queue.unfinished_tasks > 0:
                work_queue.task_done()

def dir_requester(link, wordlist, recursive, valid_codes, current_depth=0): #Process a single URL
    global content_hashes
    with visited_lock:
        if link in visited:
            return
        visited.add(link)
    try:
        resp = requests.get(link, timeout=5)
        if resp.status_code in valid_codes:
            if args.detect_duplicates: #Calculate the hash of the content
                content_hash = hashlib.md5(resp.content).hexdigest()
                
                duplicate_of = None
                with content_hash_lock:
                    if content_hash in content_hashes:
                        duplicate_of = content_hashes[content_hash] #This is a duplicate of another page
                    else:
                        content_hashes[content_hash] = link  #First time seeing this content
                
                if duplicate_of: #Dont recurse into duplicates
                    return
                else:
                    cprint(f"{resp.status_code} {link}", "light_green")
            else:
                cprint(f"{resp.status_code} {link}", "light_green")

            if recursive and (resp.status_code in valid_codes) and (current_depth + 1 <= MAX_RECURSIVE_DEPTH):
                dir_traveler(link, wordlist, recursive, valid_codes, current_depth + 1)
    except requests.RequestException:
        pass

def dir_traveler(url, wordlist, recursive, valid_codes, current_depth=0):
    if current_depth > MAX_RECURSIVE_DEPTH:
        return
    url = url.rstrip('/')
    try:
        with open(wordlist, 'r') as file:
            for line in file:
                word = line.strip()
                if not word:  # Skip empty lines
                    continue
                link = f"{url}/{word}"
                with visited_lock:
                    if link in visited:
                        continue
                work_queue.put((link, wordlist, recursive, valid_codes, current_depth)) #Add task to queue instead of starting a new thread
    except FileNotFoundError:
        cprint(f"[!] ERROR [!]: The Wordlist {wordlist} was not found, please make sure you put the correct file path", "light_red")

parser = argparse.ArgumentParser(description='Directory Traveler')
parser.add_argument('-u', '--url', dest='targeturl', type=str, required=True, help="URL to perform Directory Enumeration against")
parser.add_argument('-w', '--wordlist', dest='wordlist', type=str, required=True, help="Wordlist to use for enumeration")
parser.add_argument('-r', '--recursive', dest='recursive', action='store_true', help="Enable recursive enumeration")
parser.add_argument('-c', '--codes', dest='valid_codes', nargs='+', type=int, default=[i for i in range(200, 400)], help="Valid HTTP status codes (space-separated, ex:'200 301 302') to consider as a positive response (default: 200-399)")
parser.add_argument('-d', '--depth', dest='max_depth', type=int, default=3, help="Maximum recursive depth, anything beyond 1 is resource intensive (default: 1)")
parser.add_argument('-t', '--threads', dest='thread_count', type=int, default=10, help="Number of threads to use, be cautious when choosing this number (default: 10)")
parser.add_argument('--detect-duplicates', dest='detect_duplicates', action='store_true',help="Detect and mark duplicate content across different URLs (default: True)")
parser.add_argument('--no-detect-duplicates', dest='detect_duplicates', action='store_false', help="Disable duplicate content detection (not recommended)")
parser.set_defaults(detect_duplicates=True)  #Enabled duplicate detection by default
args = parser.parse_args()

MAX_RECURSIVE_DEPTH = args.max_depth
MAX_WORKERS = args.thread_count

cprint("[*] Starting directory scanning.......", "light_magenta")
try:
    workers = [] #Create the worker threads
    for _ in range(MAX_WORKERS):
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        workers.append(thread)

    dir_traveler(args.targeturl, args.wordlist, args.recursive, args.valid_codes)  #Start the initial scan
    last_count = 0   #Monitoring loop
    no_progress_count = 0
    while True:
        current_count = len(visited)
        queue_size = work_queue.qsize()
        new_urls = current_count - last_count
        
        cprint(f"\r[*] Queue: {queue_size} | URLs visited: {current_count} (+{new_urls})", end="")         #Show progress
        
        if new_urls > 0:
            no_progress_count = 0 #Reset no progress counter if we found new URLs
        else:
            no_progress_count += 1
        
        if queue_size == 0 and no_progress_count > 10: #Exit if queue empty and no new URLs for a while
            break
            
        last_count = current_count
        time.sleep(1)  #Sleep for a bit to avoid spamming the console
    
    for _ in range(MAX_WORKERS): #Final cleanup
        work_queue.put(None)  #Signal workers to exit
    
    for worker in workers:
        worker.join(timeout=1)
        
    cprint(f"\n[+] Scan complete! Found {len(content_hashes)} URLs ({len(visited)} visited in total)", "blue")
    
        
except KeyboardInterrupt:
    cprint(f"\n[*] Scan interrupted... Found {len(content_hashes)} URLs ({len(visited)} visited in total)", "light_yellow")
    cprint("[-] Exiting.....", "red")