from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    ips = []
    error = None
    
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        service_type = request.form.get('service_type', 'explicit-proxy')
        
        if not token:
            error = "Please provide a valid API token."
        else:
            # Prisma Access Central API Endpoint
            url = "https://api.prismacentral.paloaltonetworks.com/api/v1.0/getipaddresses"
            headers = {
                "Header-Key": token,
                "Content-Type": "application/json"
            }
            payload = {
                "serviceType": service_type,
                "addrType": "public"
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    # Safe parsing logic for the nested IP address list
                    if data.get("status") == "success" and "result" in data:
                        service_data = data["result"].get(service_type, {})
                        ips = service_data.get("ip_address", [])
                        if not ips:
                            error = f"No public IP addresses found for service type: {service_type}."
                    else:
                        error = data.get("message", "API returned an unexpected response format.")
                else:
                    error = f"API Error (Status {response.status_code}): {response.text}"
            except Exception as e:
                error = f"Failed to connect to Prisma Access API: {str(e)}"
                
    return render_template('index.html', ips=ips, error=error)

if __name__ == '__main__':
    app.run(debug=True)
