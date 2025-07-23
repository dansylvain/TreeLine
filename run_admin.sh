#!/bin/bash

# TreeLine Admin Interface Runner
# This script runs the Streamlit admin interface for TreeLine

echo "🔧 Starting TreeLine Admin Interface..."
echo "📍 Admin interface will be available at: http://localhost:8502"
echo ""
echo "💡 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop the admin interface"
echo ""

# Change to the ui directory and run the admin app
cd ui && streamlit run admin_app.py --server.port=8502 --server.headless=true
