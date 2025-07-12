# 🔧 Troubleshooting Guide

## Docker Build Issues

### Issue: pip install fails during Docker build

**Error**: `process "/bin/sh -c pip install --no-cache-dir -r requirements.txt" did not complete successfully`

**Solutions**:

1. **Use Minimal Requirements** (Recommended for initial deployment):
   ```bash
   # Use the minimal Dockerfile
   docker build -f Dockerfile.minimal -t property-intelligence-ai .
   ```

2. **Update Railway Configuration**:
   ```json
   {
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "Dockerfile.minimal"
     }
   }
   ```

3. **Alternative: Use requirements-minimal.txt**:
   - Copy `requirements-minimal.txt` to `requirements.txt`
   - Rebuild with standard Dockerfile

### Common Dependency Issues

1. **LangChain Version Conflicts**:
   - The original `langchain==0.0.340` is very old
   - Updated to `langchain>=0.1.0` for better compatibility

2. **Pandas/Numpy Conflicts**:
   - Updated to more recent versions
   - Using `>=` instead of `==` for flexibility

3. **System Dependencies**:
   - Added `libpq-dev` for PostgreSQL support
   - Added `setuptools` and `wheel` for better package installation

## Railway Deployment Issues

### Build Fails
1. Check Railway logs for specific error messages
2. Try the minimal Dockerfile first
3. Ensure all files are committed to Git

### Runtime Errors
1. Check if the application starts properly
2. Verify environment variables are set correctly
3. Check the `/health` endpoint

## Quick Fixes

### Option 1: Minimal Deployment (Recommended)
```bash
# Use minimal requirements
cp requirements-minimal.txt requirements.txt
# Deploy normally
```

### Option 2: Alternative Dockerfile
```bash
# Use the minimal Dockerfile
# Update railway.json to use Dockerfile.minimal
```

### Option 3: Manual Dependency Resolution
```bash
# Install dependencies one by one to identify conflicts
pip install fastapi uvicorn python-dotenv requests
# Then add others as needed
```

## Success Indicators

✅ **Build Success**: Docker build completes without errors
✅ **Health Check**: `/health` endpoint returns 200 OK
✅ **Landing Page**: Root endpoint `/` shows the application
✅ **API Docs**: `/docs` endpoint is accessible

## Next Steps After Fix

1. Test locally with minimal requirements
2. Deploy to Railway with minimal setup
3. Gradually add features and dependencies
4. Monitor logs for any runtime issues

## Support

If issues persist:
1. Check Railway documentation
2. Review Docker build logs
3. Test with even more minimal setup
4. Consider using Railway's built-in Python support instead of Docker