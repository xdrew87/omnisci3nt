#!/usr/bin/env python3

import requests
import os
import json

R = "\033[31m"  # red
G = "\033[32m"  # green
C = "\033[36m"  # cyan
W = "\033[0m"  # white
Y = "\033[33m"  # yellow
M = "\033[35m"  # magenta


URLSCAN_SEARCH_API = "https://urlscan.io/api/v1/search"
URLSCAN_RESULT_URL = "https://urlscan.io/result"


def run_urlscan(domain):
    """
    Query the urlscan.io Search API to find historical scans of a domain.

    Args:
        domain (str): Target domain to search for

    Returns:
        dict: Results containing scan information or error details
    """
    print(f"\n{Y}[~] URLScan :{W}\n")

    # Get API key from environment variable if available
    api_key = os.getenv("URLSCAN_API_KEY")

    # Prepare search query
    search_query = f"domain:{domain}"

    # Prepare headers
    headers = {
        "User-Agent": "Omnisci3nt/1.0"
    }

    if api_key:
        headers["API-Key"] = api_key

    # Prepare request parameters
    params = {
        "q": search_query,
        "size": 100
    }

    try:
        response = requests.get(
            URLSCAN_SEARCH_API,
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code == 401:
            print(
                f"{R}[!] Authentication failed. Invalid or expired API key.{W}"
            )
            return {"error": "Authentication failed", "exported": False}

        if response.status_code == 429:
            print(
                f"{R}[!] Rate limit exceeded. Please try again later.{W}"
            )
            return {"error": "Rate limit exceeded", "exported": False}

        if response.status_code != 200:
            print(
                f"{R}[!] Request failed with status code: {C}{response.status_code}{W}"
            )
            return {"error": f"HTTP {response.status_code}", "exported": False}

        data = response.json()

        # Check if we have results
        if not data.get("results") or len(data["results"]) == 0:
            print(f"{Y}[~] No scans found for domain: {C}{domain}{W}")
            return {"results": [], "exported": False}

        # Display results
        results = data.get("results", [])
        print(f"{G}[+] Found {C}{len(results)}{G} scan results{W}\n")

        processed_results = []

        for idx, result in enumerate(results, 1):
            scan_data = {}

            # Extract basic information
            scan_id = result.get("_id", "N/A")
            scan_data["scan_id"] = scan_id

            # Scan metadata
            task = result.get("task", {})
            scan_date = task.get("time", "N/A")
            scan_data["scan_date"] = scan_date

            scanned_url = task.get("url", "N/A")
            scan_data["scanned_url"] = scanned_url

            # Result details
            page = result.get("page", {})
            page_title = page.get("title", "N/A")
            scan_data["page_title"] = page_title

            # Server information
            server = page.get("server", "N/A")
            scan_data["server"] = server

            # IP information
            ip_address = page.get("ip", "N/A")
            scan_data["ip_address"] = ip_address

            # ASN information
            asn = page.get("asn", "N/A")
            if asn:
                asn_str = f"{asn.get('asnum', 'N/A')} ({asn.get('name', 'N/A')})"
            else:
                asn_str = "N/A"
            scan_data["asn"] = asn_str

            # Country information
            country = page.get("country", "N/A")
            scan_data["country"] = country

            # URLs
            result_url = f"{URLSCAN_RESULT_URL}/{scan_id}"
            scan_data["result_url"] = result_url

            # Screenshot URL
            screenshot_url = f"{URLSCAN_RESULT_URL}/{scan_id}/screenshot.png"
            scan_data["screenshot_url"] = screenshot_url

            # Print formatted output
            print(f"{M}[Scan #{idx}]{W}")
            print(f"{G}[+] {C}Scan ID: {W}{scan_id}")
            print(f"{G}[+] {C}Scan Date: {W}{scan_date}")
            print(f"{G}[+] {C}Scanned URL: {W}{scanned_url}")
            print(f"{G}[+] {C}Page Title: {W}{page_title}")
            print(f"{G}[+] {C}IP Address: {W}{ip_address}")
            print(f"{G}[+] {C}ASN: {W}{asn_str}")
            print(f"{G}[+] {C}Web Server: {W}{server}")
            print(f"{G}[+] {C}Country: {W}{country}")
            print(f"{G}[+] {C}Result URL: {W}{result_url}")
            print(f"{G}[+] {C}Screenshot: {W}{screenshot_url}")
            print()

            processed_results.append(scan_data)

        return {
            "results": processed_results,
            "total": len(results),
            "exported": True
        }

    except requests.exceptions.Timeout:
        print(
            f"{R}[!] Request timed out. URLScan server took too long to respond.{W}"
        )
        return {"error": "Request timed out", "exported": False}

    except requests.exceptions.ConnectionError as e:
        print(
            f"{R}[!] Connection error: {C}{str(e)}{W}"
        )
        return {"error": "Connection error", "exported": False}

    except ValueError as e:
        print(
            f"{R}[!] Invalid JSON response: {C}{str(e)}{W}"
        )
        return {"error": "Invalid JSON response", "exported": False}

    except Exception as e:
        print(
            f"{R}[!] Exception: {C}{str(e)}{W}"
        )
        return {"error": str(e), "exported": False}


if __name__ == "__main__":
    test_domain = input("Enter domain to scan: ")
    results = run_urlscan(test_domain)
    if results.get("exported"):
        print(f"\n{G}[+] Total scans found: {results['total']}")
