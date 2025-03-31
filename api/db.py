import os
from supabase import create_client, Client

POSTGRES_URL="postgres://postgres.ymhqxdxgjmkqqnogyaxx:gRNRbBi3FNvd2JTM@aws-0-eu-west-2.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x"
POSTGRES_PRISMA_URL="postgres://postgres.ymhqxdxgjmkqqnogyaxx:gRNRbBi3FNvd2JTM@aws-0-eu-west-2.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x"
SUPABASE_URL="https://ymhqxdxgjmkqqnogyaxx.supabase.co"
NEXT_PUBLIC_SUPABASE_URL="https://ymhqxdxgjmkqqnogyaxx.supabase.co"
POSTGRES_URL_NON_POOLING="postgres://postgres.ymhqxdxgjmkqqnogyaxx:gRNRbBi3FNvd2JTM@aws-0-eu-west-2.pooler.supabase.com:5432/postgres?sslmode=require"
SUPABASE_JWT_SECRET="jQXOLyGohIFgF8zwyMr3ATgvse9C6L4b792/opLocrNZzzsJOx43Pf3sHHro+6z5vKGDmkbvMhRC7IY3lrcbPw=="
POSTGRES_USER="postgres"
NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltaHF4ZHhnam1rcXFub2d5YXh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMzNzAwOTYsImV4cCI6MjA1ODk0NjA5Nn0.igwPOKAqXoot3OnE6n3W1rti3GhAaHj6K-rqiUi_3lA"
POSTGRES_PASSWORD="gRNRbBi3FNvd2JTM"
POSTGRES_DATABASE="postgres"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltaHF4ZHhnam1rcXFub2d5YXh4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzM3MDA5NiwiZXhwIjoyMDU4OTQ2MDk2fQ.Zx8ShbefCCIE87PN02n1XGCtc5XItVP009Hr2RW9kFw"
POSTGRES_HOST="db.ymhqxdxgjmkqqnogyaxx.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltaHF4ZHhnam1rcXFub2d5YXh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMzNzAwOTYsImV4cCI6MjA1ODk0NjA5Nn0.igwPOKAqXoot3OnE6n3W1rti3GhAaHj6K-rqiUi_3lA"



class SupabaseClient:
    def __init__(self):
        self.url: str = SUPABASE_URL
        self.key: str = SUPABASE_ANON_KEY
        self.client: Client = create_client(self.url, self.key)
        
    def get_client(self):
        return self.client

supabase = SupabaseClient().get_client()