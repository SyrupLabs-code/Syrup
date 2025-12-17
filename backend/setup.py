from setuptools import setup, find_packages

setup(
    name="syrup",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.1",
        "solders>=0.18.1",
        "solana>=0.30.2",
        "anchorpy>=0.18.0",
        "anthropic>=0.7.8",
        "openai>=1.3.7",
        "httpx>=0.25.2",
        "websockets>=12.0",
    ],
    python_requires=">=3.10",
)

