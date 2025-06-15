# P3IF Installation Guide

This guide provides detailed instructions for installing and setting up the P3IF (Properties, Processes, and Perspectives Inter-Framework) system.

## System Requirements

### Minimum Requirements

- **Operating System**: Linux (Ubuntu 18.04+, CentOS 7+), macOS 10.14+, or Windows 10
- **Python**: Version 3.8 or higher
- **Memory**: 4 GB RAM minimum, 8 GB recommended
- **Storage**: 2 GB available disk space
- **Network**: Internet connection for downloading dependencies

### Recommended Requirements

- **Python**: Version 3.9 or 3.10
- **Memory**: 16 GB RAM for large datasets
- **Storage**: 10 GB available disk space
- **CPU**: Multi-core processor for parallel processing

### Dependencies

The following system dependencies are required:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv git curl
sudo apt-get install build-essential libssl-dev libffi-dev
```

**CentOS/RHEL:**
```bash
sudo yum update
sudo yum install python3-devel python3-pip git curl
sudo yum groupinstall "Development Tools"
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 git
```

**Windows:**
- Install Python 3.8+ from [python.org](https://python.org)
- Install Git from [git-scm.com](https://git-scm.com)
- Install Visual Studio Build Tools or Visual Studio Community

## Installation Methods

### Method 1: Standard Installation (Recommended)

1. **Clone the Repository**

   ```bash
   git clone https://github.com/p3if/p3if.git
   cd p3if
   ```

2. **Create Virtual Environment**

   ```bash
   python3 -m venv venv
   
   # Activate virtual environment
   # On Linux/macOS:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run Setup Script**

   ```bash
   python setup.py install
   ```

5. **Verify Installation**

   ```bash
   python -c "import p3if; print(p3if.__version__)"
   ```

### Method 2: Development Installation

For developers who want to contribute to P3IF:

1. **Fork and Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/p3if.git
   cd p3if
   ```

2. **Create Development Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install in Development Mode**

   ```bash
   pip install -e .
   ```

4. **Run Tests**

   ```bash
   pytest tests/
   ```

### Method 3: Docker Installation

For containerized deployment:

1. **Install Docker**

   Follow the official Docker installation guide for your operating system.

2. **Pull P3IF Image**

   ```bash
   docker pull p3if/p3if:latest
   ```

3. **Run Container**

   ```bash
   docker run -p 5000:5000 -v $(pwd)/data:/app/data p3if/p3if:latest
   ```

4. **Access Application**

   Open your browser and navigate to `http://localhost:5000`

### Method 4: Using Docker Compose

For a complete development environment:

1. **Clone Repository**

   ```bash
   git clone https://github.com/p3if/p3if.git
   cd p3if
   ```

2. **Start Services**

   ```bash
   docker-compose up -d
   ```

3. **Check Status**

   ```bash
   docker-compose ps
   ```

## Configuration

### Basic Configuration

Create a configuration file at `config/config.yaml`:

```yaml
# P3IF Configuration
app:
  name: "P3IF"
  version: "1.0.0"
  debug: false
  host: "0.0.0.0"
  port: 5000

database:
  type: "sqlite"
  path: "data/p3if.db"
  # For PostgreSQL:
  # type: "postgresql"
  # host: "localhost"
  # port: 5432
  # name: "p3if"
  # user: "p3if_user"
  # password: "your_password"

data:
  default_domain_path: "data/domains"
  synthetic_data_path: "data/synthetic"
  export_path: "data/exports"

visualization:
  default_width: 800
  default_height: 600
  cache_enabled: true
  cache_path: "data/viz_cache"

logging:
  level: "INFO"
  file: "logs/p3if.log"
  max_size: "10MB"
  backup_count: 5
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Environment Configuration
P3IF_CONFIG_PATH=config/config.yaml
P3IF_DEBUG=false
P3IF_SECRET_KEY=your-secret-key-here
P3IF_DATABASE_URL=sqlite:///data/p3if.db

# API Configuration
P3IF_API_HOST=0.0.0.0
P3IF_API_PORT=5000
P3IF_API_TOKEN=your-api-token

# Visualization Settings
P3IF_VIZ_CACHE_ENABLED=true
P3IF_VIZ_DEFAULT_THEME=default
```

### Database Setup

#### SQLite (Default)

SQLite is used by default and requires no additional setup. The database file will be created automatically.

#### PostgreSQL

1. **Install PostgreSQL**

   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # CentOS/RHEL
   sudo yum install postgresql-server postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create Database and User**

   ```sql
   sudo -u postgres psql
   CREATE DATABASE p3if;
   CREATE USER p3if_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE p3if TO p3if_user;
   \q
   ```

3. **Update Configuration**

   Update `config/config.yaml` with PostgreSQL settings.

4. **Initialize Database**

   ```bash
   python scripts/init_database.py
   ```

## Initial Setup

### 1. Generate Sample Data

```bash
python scripts/generate_sample_data.py
```

### 2. Create First Domain

```bash
python scripts/create_domain.py --name "cybersecurity" --description "Cybersecurity framework"
```

### 3. Start the Application

```bash
python app.py
```

### 4. Access Web Interface

Open your browser and navigate to `http://localhost:5000`

## Verification

### Test Basic Functionality

```bash
# Test data generation
python scripts/test_data_generation.py

# Test visualization
python scripts/test_visualization.py

# Test API
curl http://localhost:5000/api/v1/domains
```

### Run Full Test Suite

```bash
pytest tests/ -v
```

### Check System Health

```bash
python scripts/health_check.py
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues

**Problem**: `ImportError` or syntax errors
**Solution**: Ensure Python 3.8+ is installed and activated

```bash
python --version
which python
```

#### 2. Permission Errors

**Problem**: Permission denied when installing packages
**Solution**: Use virtual environment or user install

```bash
pip install --user -r requirements.txt
```

#### 3. Missing System Dependencies

**Problem**: Failed building wheel for package
**Solution**: Install system development tools

```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel
```

#### 4. Port Already in Use

**Problem**: Port 5000 is already in use
**Solution**: Change port in configuration or kill conflicting process

```bash
# Find process using port 5000
lsof -i :5000

# Kill process (replace PID)
kill -9 PID

# Or change port in config
export P3IF_API_PORT=5001
```

#### 5. Database Connection Issues

**Problem**: Cannot connect to database
**Solution**: Check database service and credentials

```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test connection
psql -h localhost -U p3if_user -d p3if
```

### Getting Help

If you encounter issues not covered here:

1. Check the [FAQ](../FAQ.md)
2. Search existing [GitHub Issues](https://github.com/p3if/p3if/issues)
3. Create a new issue with:
   - Operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

## Updating P3IF

### Standard Update

```bash
cd p3if
git pull origin main
pip install -r requirements.txt
python scripts/migrate_database.py  # If database changes
```

### Docker Update

```bash
docker pull p3if/p3if:latest
docker-compose down
docker-compose up -d
```

## Uninstallation

### Standard Installation

```bash
pip uninstall p3if
rm -rf /path/to/p3if
```

### Docker Installation

```bash
docker-compose down
docker rmi p3if/p3if:latest
```

## Performance Optimization

### For Large Datasets

1. **Increase Memory**
   ```bash
   export PYTHONHASHSEED=0
   export OMP_NUM_THREADS=4
   ```

2. **Enable Caching**
   ```yaml
   visualization:
     cache_enabled: true
     cache_size: 1000
   ```

3. **Use PostgreSQL**
   Switch from SQLite to PostgreSQL for better performance with large datasets.

4. **Parallel Processing**
   ```bash
   export P3IF_WORKERS=4
   ```

### Memory Management

```bash
# Monitor memory usage
python scripts/memory_monitor.py

# Optimize for memory-constrained environments
export P3IF_LOW_MEMORY=true
```

## Security Considerations

### Production Deployment

1. **Change Default Secrets**
   ```bash
   export P3IF_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   ```

2. **Use HTTPS**
   Configure reverse proxy (nginx/Apache) with SSL certificates

3. **Database Security**
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access

4. **API Security**
   - Implement proper authentication
   - Use rate limiting
   - Validate all inputs

For production deployment, see the [Deployment Guide](deployment.md). 