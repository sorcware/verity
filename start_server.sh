# calls mdbooks to run in the backgroun
echo "Starting mdbook to run in the background"
mdbook serve docs &

echo "Starting Verity"
uv run verity.py
