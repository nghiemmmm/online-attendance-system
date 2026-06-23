$ErrorActionPreference = "Stop"
Write-Host "Creating frontend directory..."
New-Item -ItemType Directory -Force -Path "frontend"
Set-Location "frontend"

Write-Host "Initializing Next.js..."
npx -y create-next-app@latest . --ts --tailwind --eslint --app --use-npm --yes

Write-Host "Installing shadcn dependencies..."
npm install clsx tailwind-merge lucide-react @radix-ui/react-slot @radix-ui/react-avatar class-variance-authority

Write-Host "Copying files from frontend-design..."
Copy-Item -Path "..\frontend-design\app\*" -Destination "app" -Recurse -Force
Copy-Item -Path "..\frontend-design\components\*" -Destination "components" -Recurse -Force
Copy-Item -Path "..\frontend-design\lib\*" -Destination "lib" -Recurse -Force
Copy-Item -Path "..\frontend-design\types\*" -Destination "types" -Recurse -Force
Copy-Item -Path "..\frontend-design\services\*" -Destination "services" -Recurse -Force

Write-Host "Starting dev server..."
npm run dev
