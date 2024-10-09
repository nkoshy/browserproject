# Browserapp

Spin up a Firefox browser instance in Kubernetes with a single API request.

## Description

Browserapp is a Python Flask-based application deployed in Kubernetes that creates a Firefox browser instance as a pod upon receiving an API request. It returns a URL that allows users to access the browser instance directly from their laptop browser.

## Features

- Quickly spin up Firefox browser instances in the cloud
- Access browser instances through a simple URL
- No specific configuration required
- Utilizes Firefox Docker image for pod creation
- Deployed as a Kubernetes application
- Accessible via Ingress

## Prerequisites

- Kubernetes cluster
- kubectl configured to communicate with your cluster
- Ingress controller set up in your cluster

## Deployment

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/browserapp.git
   cd browserapp
   ```

2. Apply the Kubernetes manifests:
   ```
   kubectl apply -f k8s/
   ```

This will deploy the Browserapp along with necessary services and ingress rules.

## Usage

1. Once deployed, access the application through the Ingress URL. You can find this URL by checking your Ingress resource:
   ```
   kubectl get ingress
   ```

2. Send a POST request to the `/spin` endpoint using the Ingress URL:
   ```
   curl -X POST http://your-ingress-url/spin
   ```

3. The API will return a URL. Use this URL in your laptop's browser to access the Firefox instance.

## API Endpoints

- `POST /spin`: Spins up a new Firefox browser instance and returns the access URL.

## Configuration

No specific configuration is required for basic usage. The application uses default settings to create the Firefox pod in your Kubernetes cluster. For advanced configuration, refer to the Kubernetes manifests in the `k8s/` directory.

## Docker

The application uses the official Firefox Docker image to create the browser instance pods.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have any questions, please open an issue in the GitHub repository.
