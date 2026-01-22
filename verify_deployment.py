"""
Script to verify deployment and check for any errors
"""
import subprocess
import sys

print("=" * 60)
print("DEPLOYMENT VERIFICATION")
print("=" * 60)

# Check git status
print("\n1. Git Status:")
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
if result.stdout.strip():
    print("⚠️  Uncommitted changes:")
    print(result.stdout)
else:
    print("✅ All changes committed")

# Check last commit
print("\n2. Last Commit:")
result = subprocess.run(['git', 'log', '-1', '--oneline'], capture_output=True, text=True)
print(result.stdout.strip())

# Check remote status
print("\n3. Remote Status:")
result = subprocess.run(['git', 'status', '-sb'], capture_output=True, text=True)
print(result.stdout.strip())

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("1. Go to: https://vercel.com/dashboard")
print("2. Check your project's latest deployment")
print("3. Wait for 'Ready' status (usually 2-3 minutes)")
print("4. Click 'Visit' to see live site")
print("=" * 60)
