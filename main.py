import requests
from dotenv import load_dotenv
import os
import argparse


# Load the environment variables from the .env file
load_dotenv()

# Get the API key and secret from environment variables
ENDOR_NAMESPACE = os.getenv("ENDOR_NAMESPACE")
API_URL = 'https://api.endorlabs.com/v1'

def get_token():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    url = f"{API_URL}/auth/api-key"
    payload = {
        "key": api_key,
        "secret": api_secret
    }
    headers = {
        "Content-Type": "application/json",
        "Request-Timeout": "60"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=60)
    
    if response.status_code == 200:
        token = response.json().get('token')
        return token
    else:
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

API_TOKEN = get_token()
HEADERS = {
    "User-Agent": "curl/7.68.0",
    "Accept": "*/*",
    "Authorization": f"Bearer {API_TOKEN}",
    "Request-Timeout": "600"  # Set the request timeout to 60 seconds
}

def get_github_actions_packages():
    print("Fetching GitHub Actions packages...")
    query_data = {
        "tenant_meta": {
            "namespace": ""
        },
        "meta": {
            "name": "Get all GitHub Actions packages"
        },
        "spec": {
            "query_spec": {
                "kind": "PackageVersion",
                "list_parameters": {
                    "filter": "spec.ecosystem==ECOSYSTEM_GITHUB_ACTION",
                    "mask": "uuid,spec.project_uuid,tenant_meta",
                    "traverse": True
                }
            }
        }
    }

    # Define the queries endpoint URL
    url = f"{API_URL}/namespaces/{ENDOR_NAMESPACE}/queries"
    print(f"POST Request to URL: {url}")
    print(f"Using filter: {query_data['spec']['query_spec']['list_parameters']['filter']}")

    github_actions_packages = []
    next_page_id = None

    try:
        while True:
            if next_page_id:
                query_data["spec"]["query_spec"]["list_parameters"]["page_token"] = next_page_id

            # Make the POST request to the queries endpoint
            response = requests.post(url, headers=HEADERS, json=query_data, timeout=600)

            if response.status_code != 200:
                print(f"Failed to fetch GitHub Actions packages. Status Code: {response.status_code}, Response: {response.text}")
                return []

            # Parse the response data
            response_data = response.json()
            packages = response_data.get("spec", {}).get("query_response", {}).get("list", {}).get("objects", [])

            # Process the results
            for package in packages:
                package_uuid = package.get("uuid")
                tenant_name = package.get("tenant_meta", {}).get("namespace")
                project_uuid = package.get("spec", {}).get("project_uuid")
                relative_path = package.get("spec", {}).get("relative_path")
                github_actions_packages.append(package)
                print(f"Found GitHub Actions package: {package_uuid}, tenant-name: {tenant_name}, project-uuid: {project_uuid}, relative_path: {relative_path}")

            # Check for next page
            next_page_id = response_data.get("spec", {}).get("query_response", {}).get("list", {}).get("response", {}).get("next_page_token")
            if not next_page_id:
                break

        return list(github_actions_packages)

    except requests.RequestException as e:
        print(f"An error occurred while fetching GitHub Actions packages: {e}")
        return []


def delete_github_actions_packages(github_actions_packages):
    print("Attempting to delete GitHub Actions packages...")
    for package in github_actions_packages:
        package_uuid = package.get("uuid")
        tenant_name = package.get("tenant_meta", {}).get("namespace")

        if package_uuid and tenant_name:
            url = f"{API_URL}/namespaces/{tenant_name}/package-versions/{package_uuid}"
            try:
                print(f"Deleting GitHub Actions package with UUID: {package_uuid}")
                response = requests.delete(url, headers=HEADERS, timeout=60)
                if response.status_code == 200:
                    print(f"Successfully deleted package with UUID: {package_uuid}")
                else:
                    print(f"Failed to delete package with UUID: {package_uuid}. Status Code: {response.status_code}, Response: {response.text}")
            except requests.RequestException as e:
                print(f"An error occurred while deleting package with UUID: {package_uuid}: {e}")
        else:
            print(f"Skipping package: Missing UUID or tenant name. Package details: {package}")


def get_github_actions_findings():
    print("Fetching GitHub Actions findings...")
    query_data = {
        "tenant_meta": {
            "namespace": ""
        },
        "meta": {
            "name": "Get all GitHub Actions findings"
        },
        "spec": {
            "query_spec": {
                "kind": "Finding",
                "list_parameters": {
                    "filter": "spec.finding_categories contains 'FINDING_CATEGORY_GHACTIONS'",
                    "mask": "uuid,spec.project_uuid,spec.summary,tenant_meta",
                    "traverse": True
                }
            }
        }
    }

    # Define the queries endpoint URL
    url = f"{API_URL}/namespaces/{ENDOR_NAMESPACE}/queries"
    print(f"POST Request to URL: {url}")
    print(f"Using filter: {query_data['spec']['query_spec']['list_parameters']['filter']}")

    github_actions_findings = []
    next_page_id = None
    page_count = 0
    max_pages = 1000  # Safety limit to prevent infinite loops
    previous_page_token = None
    same_token_count = 0

    try:
        while page_count < max_pages:
            if next_page_id:
                query_data["spec"]["query_spec"]["list_parameters"]["page_token"] = next_page_id

            print(f"Fetching page {page_count + 1}...")
            # Make the POST request to the queries endpoint
            response = requests.post(url, headers=HEADERS, json=query_data, timeout=600)

            if response.status_code != 200:
                print(f"Failed to fetch GitHub Actions findings. Status Code: {response.status_code}, Response: {response.text}")
                return []

            # Parse the response data
            response_data = response.json()
            findings = response_data.get("spec", {}).get("query_response", {}).get("list", {}).get("objects", [])
            
            print(f"Found {len(findings)} findings on page {page_count + 1}")

            # Process the results
            for finding in findings:
                finding_uuid = finding.get("uuid")
                tenant_name = finding.get("tenant_meta", {}).get("namespace")
                project_uuid = finding.get("spec", {}).get("project_uuid")
                summary = finding.get("spec", {}).get("summary", "No summary available")
                github_actions_findings.append(finding)
                print(f"Found GitHub Actions finding: {finding_uuid}, tenant-name: {tenant_name}, project-uuid: {project_uuid}")
                print(f"  Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")

            # Check for next page
            next_page_id = response_data.get("spec", {}).get("query_response", {}).get("list", {}).get("response", {}).get("next_page_token")
            print(f"Next page token: {next_page_id}")
            
            # Check if we're getting the same token repeatedly (API bug detection)
            if next_page_id == previous_page_token:
                same_token_count += 1
                if same_token_count >= 3:  # If we get the same token 3 times in a row, stop
                    print(f"Detected API pagination bug: same token '{next_page_id}' returned {same_token_count} times. Stopping.")
                    break
            else:
                same_token_count = 0  # Reset counter if token changes
            
            previous_page_token = next_page_id
            
            if not next_page_id:
                print("No more pages to fetch.")
                break
                
            page_count += 1

        if page_count >= max_pages:
            print(f"Warning: Reached maximum page limit ({max_pages}). Stopping to prevent infinite loop.")

        return list(github_actions_findings)

    except requests.RequestException as e:
        print(f"An error occurred while fetching GitHub Actions findings: {e}")
        return []


def delete_github_actions_findings(github_actions_findings):
    print("Attempting to delete GitHub Actions findings...")
    for finding in github_actions_findings:
        finding_uuid = finding.get("uuid")
        tenant_name = finding.get("tenant_meta", {}).get("namespace")

        if finding_uuid and tenant_name:
            url = f"{API_URL}/namespaces/{tenant_name}/findings/{finding_uuid}"
            try:
                print(f"Deleting GitHub Actions finding with UUID: {finding_uuid}")
                response = requests.delete(url, headers=HEADERS, timeout=60)
                if response.status_code == 200:
                    print(f"Successfully deleted finding with UUID: {finding_uuid}")
                else:
                    print(f"Failed to delete finding with UUID: {finding_uuid}. Status Code: {response.status_code}, Response: {response.text}")
            except requests.RequestException as e:
                print(f"An error occurred while deleting finding with UUID: {finding_uuid}: {e}")
        else:
            print(f"Skipping finding: Missing UUID or tenant name. Finding details: {finding}")


def main():
    parser = argparse.ArgumentParser(description="Fetch and potentially delete GitHub Actions packages and findings.")
    parser.add_argument('--no-dry-run', action='store_true', help="Fetch and delete all identified GitHub Actions packages and findings.")
    parser.add_argument('--packages-only', action='store_true', help="Only process GitHub Actions packages (default: process both packages and findings).")
    parser.add_argument('--findings-only', action='store_true', help="Only process GitHub Actions findings (default: process both packages and findings).")
    args = parser.parse_args()

    # Determine what to process
    process_packages = not args.findings_only
    process_findings = not args.packages_only

    if process_packages:
        github_actions_packages = get_github_actions_packages()
        print(f"Found {len(github_actions_packages)} GitHub Actions packages.")
        
        if args.no_dry_run:
            delete_github_actions_packages(github_actions_packages)
        else:
            print("Dry run mode: No packages will be deleted.")

    if process_findings:
        github_actions_findings = get_github_actions_findings()
        print(f"Found {len(github_actions_findings)} GitHub Actions findings.")
        
        if args.no_dry_run:
            delete_github_actions_findings(github_actions_findings)
        else:
            print("Dry run mode: No findings will be deleted.")

    if not args.no_dry_run:
        print("Dry run mode: No packages or findings will be deleted. To delete all identified GitHub Actions packages and findings, run the script with the --no-dry-run flag.")

if __name__ == "__main__":
    main()