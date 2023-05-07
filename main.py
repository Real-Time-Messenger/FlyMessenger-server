import uvicorn

if __name__ == "__main__":
    # TODO: Implement SSL.
    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain("app/certs/cert.pem", "app/certs/key.pem")

    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True,
        # ssl_context=ssl_context,
        # workers=1,
    )