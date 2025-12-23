# StructuDoc

**AI-Powered Document Processing and Schema Discovery Platform**

StructuDoc is an intelligent document processing system that leverages Large Language Models (LLMs) to extract, analyze, and structure content from business documents. It combines document parsing, image analysis, and schema discovery to transform unstructured documents into structured, queryable data.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Development](#development)
- [Deployment](#deployment)
- [License](#license)

## Overview

StructuDoc automates the process of extracting structured data from business documents (DOCX, PDF) using AI. It provides a complete pipeline for:

- **Document Upload & Parsing**: Convert documents to markdown with automatic image extraction
- **AI-Powered Image Analysis**: Describe and explain images using vision-enabled LLMs
- **Structured Data Extraction**: Parse document content into structured JSON using customizable prompts
- **Schema Discovery**: Identify common data structures across multiple documents
- **Cloud Storage**: Store all processed data in S3-compatible object storage (MinIO or AWS S3)

### Use Cases

- Extracting structured data from invoices, contracts, and reports
- Analyzing image content in technical documentation
- Discovering common schemas across document collections
- Automating document processing workflows
- Building document intelligence pipelines

## Key Features

### Document Processing Pipeline

- **Multi-Format Support**: Process both DOCX and PDF files
- **Automatic Conversion**: PDF to DOCX to Markdown conversion using Pandoc
- **Image Extraction**: Automatically extract and organize images from documents
- **Metadata Management**: Track processing history and versions

### AI-Powered Analysis

- **Vision-Enabled LLMs**: Describe images using Claude or other vision models
- **Customizable Prompts**: Define custom parsing instructions for different document types
- **Streaming Responses**: Real-time progress feedback during LLM processing
- **Batch Processing**: Process multiple documents simultaneously

### Schema Discovery

- **Cross-Document Analysis**: Identify common fields and structures across multiple documents
- **Schema Generation**: Automatically generate unified schema templates
- **Source Tracking**: Maintain links between schemas and source documents

### Storage & Organization

- **S3-Compatible Storage**: Works with both MinIO (self-hosted) and AWS S3
- **Structured Folders**: Organized hierarchy for each processed document
- **Version Control**: Track multiple parsing attempts with indexed results
- **Direct Access**: All data accessible via S3 APIs

## Architecture

### System Components

```
┌─────────────────┐
│   Streamlit UI  │  (Port 8501)
│   - Upload      │
│   - Parse       │
│   - Analyze     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   FastAPI       │────▶│ LLM Provider │
│   Backend       │     │ (Bedrock/    │
│   (Port 8080)   │     │  Anthropic)  │
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐
│  MinIO/S3       │
│  Object Storage │
│  (Ports 9000,   │
│   9001)         │
└─────────────────┘
```

### Data Flow

1. **Upload**: User uploads DOCX/PDF via Streamlit UI
2. **Convert**: Backend converts PDF→DOCX→Markdown using Pandoc
3. **Extract**: Images extracted from document
4. **Store**: Files organized in S3 folder structure: `structudoc_{filename}/`
5. **Parse**: LLM analyzes images and document content
6. **Structure**: Results saved as JSON in S3
7. **Discover**: Common schemas identified across multiple documents

### Folder Structure

Each processed document creates a structured folder:

```
structudoc_{filename}/
├── {filename}.docx               # Original or converted DOCX
├── {filename}.md                 # Markdown version
├── images/
│   ├── image_1.png
│   ├── image_2.png
│   └── ...
├── images_descriptions/
│   ├── images_description_1.json # First parsing attempt
│   ├── images_description_2.json # Second parsing attempt
│   └── ...
├── parsed_document/
│   ├── parsed_document_1.json    # First document parsing
│   ├── parsed_document_2.json    # Second document parsing
│   └── ...
└── common_schemas/
    ├── common_schema_1.json      # Schema discovered across docs
    └── ...
```

## Technology Stack

### Backend

- **Framework**: FastAPI (Python web framework)
- **Document Processing**: Pandoc, pdf2docx, python-docx
- **LLM Integration**: LangChain, LangChain AWS, LangChain Anthropic
- **Storage**: boto3 (AWS S3), MinIO SDK
- **Python Version**: 3.12

### Frontend

- **UI Framework**: Streamlit
- **Components**: st-ant-tree (file trees), streamlit-js-eval

### Infrastructure

- **Container Orchestration**: Docker Compose
- **Object Storage**: MinIO (local) or AWS S3 (cloud)
- **System Dependencies**: Pandoc, TeXLive

### LLM Providers

- **AWS Bedrock**: Claude via AWS
- **Anthropic**: Direct Claude API access
- **Configurable**: Easy to add other providers

## Getting Started

### Prerequisites

- Docker and Docker Compose
- (Optional) AWS account for S3 or Bedrock
- (Optional) Anthropic API key for direct Claude access

### Quick Start

1. **Clone the repository**

```bash
git clone <repository-url>
cd StructuDoc
```

2. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Environment
ENV=local                    # Use 'local' for development

# Security
SECRET_KEY=your-secret-key-here
FAST_API_ACCESS_SECRET_TOKEN=your-token-here

# Storage Configuration
SOURCE_BUCKET=minio/source-bucket    # or s3/your-bucket-name
AWS_ACCESS_KEY_ID=admin
AWS_SECRET_ACCESS_KEY=password
AWS_REGION=us-east-1

# MinIO Configuration (for local development)
MINIO_HOST=http://minio:9000
MINIO_SECURE=false

# LLM Configuration
LLM_MODEL=Bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0
# OR
# LLM_MODEL=Anthropic:claude-3-5-sonnet-20241022
# ANTHROPIC_API_KEY=your-api-key-here
```

3. **Start the application**

```bash
# Development mode (with live reload)
docker-compose up

# Production mode (using pre-built images)
docker-compose -f docker-compose-prod.yml up
```

4. **Access the application**

- **Streamlit UI**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8080
- **MinIO Console**: http://localhost:9001 (login: admin/password)
- **MinIO API**: http://localhost:9000

### Using Just (Optional)

If you have [Just](https://github.com/casey/just) installed:

```bash
just local      # Start development environment
just prod       # Start production environment
just prod_image # Build and push Docker images
```

## Configuration

### Environment Variables

#### Core Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENV` | Deployment environment | `local` | Yes |
| `SECRET_KEY` | Session middleware key | - | Yes |
| `FAST_API_ACCESS_SECRET_TOKEN` | API authentication token | - | Yes |

#### Storage Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `SOURCE_BUCKET` | Storage backend and bucket | `minio/source-bucket` or `s3/my-bucket` |
| `AWS_ACCESS_KEY_ID` | S3/MinIO access key | `admin` |
| `AWS_SECRET_ACCESS_KEY` | S3/MinIO secret key | `password` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `MINIO_HOST` | MinIO server URL | `http://minio:9000` |
| `MINIO_SECURE` | Use SSL/TLS for MinIO | `false` |

#### LLM Configuration

| Variable | Format | Example |
|----------|--------|---------|
| `LLM_MODEL` | `{provider}:{model-id}` | `Bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0` |
| | | `Anthropic:claude-3-5-sonnet-20241022` |
| `ANTHROPIC_API_KEY` | API key for Anthropic | `sk-ant-...` |

### Storage Backends

#### MinIO (Local Development)

Best for local development and testing:

```bash
SOURCE_BUCKET=minio/source-bucket
MINIO_HOST=http://minio:9000
MINIO_SECURE=false
AWS_ACCESS_KEY_ID=admin
AWS_SECRET_ACCESS_KEY=password
```

#### AWS S3 (Production)

For production deployments:

```bash
SOURCE_BUCKET=s3/your-production-bucket
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

### LLM Providers

#### AWS Bedrock

```bash
LLM_MODEL=Bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0
# Use AWS credentials configured above
```

#### Anthropic Direct

```bash
LLM_MODEL=Anthropic:claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## Usage

### 1. Upload Documents

Navigate to **Upload Source Files** page:

1. Choose upload method:
   - Upload new files from your computer
   - Parse existing files from S3
2. Select DOCX or PDF files
3. Click "Upload and Process"

The system will:
- Convert PDFs to DOCX (if needed)
- Generate markdown with Pandoc
- Extract images
- Store everything in organized S3 folders

### 2. View Processed Files

Go to **Parse Files With LLM** → **View Files** tab:

- Browse processed folders
- View markdown content with embedded images
- Examine extracted images
- Review previous parsing results

### 3. Describe Images with AI

**Parse Files With LLM** → **Parse Image With LLM** tab:

1. Select a folder containing images
2. Choose a prompt:
   - **Default**: "Describe The Image"
   - **Custom**: Enter your own prompt
3. Click "Parse Images"
4. Watch streaming responses in real-time
5. Results saved to `images_descriptions/`

### 4. Parse Documents to JSON

**Parse Files With LLM** → **Parse File With LLM** tab:

1. Select a processed folder
2. Choose or create a custom prompt
3. Optional: Include image descriptions in parsing
4. Click "Parse File"
5. View structured JSON output
6. Save results to `parsed_document/`

**Default Prompt**:
```
Return a JSON file. Start your output with '{'.
Parse the content and return a JSON file with all
values properly formatted as JSON.
```

### 5. Discover Common Schemas

**Parse Files With LLM** → **Find Common Schema** tab:

1. Select multiple processed folders
2. Review the schema discovery prompt
3. Click "Find Common Schema"
4. View unified schema across all documents
5. Save to `common_schemas/`

This analyzes all selected documents and identifies common fields, structures, and patterns.

### 6. Review Common Schemas

**Parse Files With LLM** → **View Common Schemas** tab:

- Browse previously generated schemas
- View source documents for each schema
- Review schema structure and fields

## API Reference

### Document Processing Endpoints

#### Upload and Process File

```http
POST /upload_source_file_to_s3
Content-Type: multipart/form-data

Parameters:
- file: File (DOCX or PDF)
- file_name: string

Returns: Processing status and S3 path
```

#### Parse Existing S3 File

```http
POST /parse_s3_path
Content-Type: application/json

Body:
{
  "s3_path": "path/to/file.pdf"
}

Returns: Processing status
```

### File Retrieval Endpoints

#### List Processed Folders

```http
GET /get_all_the_folders

Returns: List of folder names
```

#### Get Markdown Content

```http
GET /get_markdown?folder_name={name}

Returns: Markdown text
```

#### Get Markdown with Embedded Images

```http
GET /get_markdown_with_images?folder_name={name}

Returns: Markdown with base64-encoded images
```

#### List Folder Images

```http
GET /get_all_the_images?folder_name={name}

Returns: List of image filenames
```

### LLM Processing Endpoints

#### Generate Image Description

```http
GET /get_image_description
  ?folder_name={name}
  &image_file_name={image}
  &prompt={custom_prompt}

Returns: Server-Sent Events stream
```

#### Parse Document with LLM

```http
GET /get_parsed_file
  ?folder_name={name}
  &prompt={custom_prompt}
  &is_images_descriptions_included={true|false}

Returns: Server-Sent Events stream
```

#### Discover Common Schema

```http
GET /get_common_schema
  ?folder_names={name1,name2,...}
  &prompt={custom_prompt}

Returns: Server-Sent Events stream
```

### Parsing Results Endpoints

#### List Image Descriptions

```http
GET /get_images_explanations_paths?folder_name={name}

Returns: List of description JSON filenames
```

#### Get Image Description

```http
GET /get_images_explanation
  ?folder_name={name}
  &file_name={filename}

Returns: JSON content
```

#### List Document Parsings

```http
GET /receive_json_parsings_paths?folder_name={name}

Returns: List of parsing JSON filenames
```

#### Get Document Parsing

```http
GET /receive_json_parsings
  ?folder_name={name}
  &file_name={filename}

Returns: JSON content
```

## Development

### Project Structure

```
StructuDoc/
├── fastapi/                      # Backend application
│   ├── document_parsing.py       # Document conversion logic
│   ├── llm_functions.py          # LLM abstraction layer
│   ├── parse_data_with_llm.py    # LLM parsing endpoints
│   ├── s3_handler.py             # S3/MinIO client
│   ├── s3_interactions.py        # S3 operations
│   └── Dockerfile                # Backend container
├── streamlit/                    # Frontend application
│   ├── pages/                    # Multi-page app
│   │   ├── 0_upload_source_files.py
│   │   └── 1_parse_files_with_llm.py
│   └── .Dockerfile               # Frontend container
├── docker-compose.yml            # Development orchestration
├── docker-compose-prod.yml       # Production orchestration
├── base.Dockerfile               # Base image with dependencies
├── justfile                      # Build automation
└── .env                          # Environment configuration
```

### Local Development Setup

1. **Install dependencies for local development**

```bash
# Backend
cd fastapi
pip install -r requirements.txt

# Frontend
cd streamlit
pip install -r requirements.txt
```

2. **Run services individually**

```bash
# Backend (development mode)
cd fastapi
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Frontend
cd streamlit
streamlit run main.py
```

3. **Or use Docker Compose with hot reload**

```bash
docker-compose up
# Changes to code will auto-reload
```

### Building Docker Images

#### Build Base Image

```bash
docker build -f base.Dockerfile -t pondered/base_structudoc:latest .
```

#### Build Application Images

```bash
# Backend
docker build -f fastapi/Dockerfile -t pondered/structudoc:latest .

# Frontend
docker build -f streamlit/.Dockerfile -t structudoc-frontend .
```

#### Multi-Platform Build (for production)

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t pondered/structudoc:latest \
  --push \
  .
```

### Testing

```bash
# Run backend tests
cd fastapi
pytest

# Test API endpoints
curl http://localhost:8080/get_all_the_folders
```

## Deployment

### Production Deployment with Docker

1. **Build and push images**

```bash
just prod_image
```

2. **Deploy with production compose**

```bash
docker-compose -f docker-compose-prod.yml up -d
```

3. **Configure production environment**

Update `.env` with production settings:
- Use AWS S3 instead of MinIO
- Set strong SECRET_KEY and FAST_API_ACCESS_SECRET_TOKEN
- Configure AWS credentials
- Set ENV to production value

### AWS Deployment Checklist

- [ ] Create S3 bucket for storage
- [ ] Configure IAM credentials with S3 access
- [ ] Set up Bedrock access (if using)
- [ ] Configure security groups for container services
- [ ] Set up load balancer for FastAPI
- [ ] Configure SSL/TLS certificates
- [ ] Set up CloudWatch logging
- [ ] Enable S3 bucket versioning
- [ ] Configure backup policies

### Monitoring

- **Health Check**: `GET http://localhost:8080/` (FastAPI)
- **MinIO Health**: `http://localhost:9000/minio/health/live`
- **Logs**: `docker-compose logs -f [service_name]`

## Security Considerations

- **API Authentication**: Use `FAST_API_ACCESS_SECRET_TOKEN` for API access
- **Storage Access**: Restrict S3/MinIO credentials to necessary permissions
- **LLM API Keys**: Rotate regularly, use AWS Secrets Manager in production
- **Network Security**: Use HTTPS in production, restrict ports
- **Data Privacy**: Ensure compliance with data protection regulations
- **File Validation**: System validates file types before processing

## Troubleshooting

### Common Issues

**Issue**: MinIO connection refused

```bash
# Check MinIO is running
docker-compose ps minio

# Check MinIO logs
docker-compose logs minio

# Verify bucket creation
docker-compose logs mc
```

**Issue**: PDF conversion fails

```bash
# Ensure Pandoc and TeXLive are installed
docker-compose exec fastapi which pandoc

# Check document format
# Some complex PDFs may need manual conversion
```

**Issue**: LLM requests timeout

```bash
# Check LLM_MODEL configuration
# Verify API credentials
# Check network connectivity to LLM provider
```

**Issue**: Images not displaying in markdown

```bash
# Verify images extracted: /get_all_the_images?folder_name=...
# Check image paths in markdown
# Ensure images are in correct S3 folder
```

## Support

For issues, questions, or contributions, please visit the project repository or contact the Ponder team.

---
