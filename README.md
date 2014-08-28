## crypter

Crypter is an encryption daemon designed to be run on a container host (i.e. Docker).
It listens to unix domain sockets for client connections, and encrypts or decrypts
values on request. This allows sensitive configuration values (i.e. credentials)
to be encrypted in a docker container and decrypted at runtime by the container
host.

An RSA private key and certificate for encryption can be generated with the
following OpenSSL command:

```
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days XXX -nodes
```

Keep your private key in a safe place, and distribute it to your container hosts
when they are built. We use puppetmaster to store the key locally and copy it to
Docker host machines during image building.

#### Running the daemon

To run the daemon, provide the location of your key files and the directory to
create unix sockets in:

```
crypter -d /var/run/crypter --key /path/to/key.pem --cert /path/to/cert.pem
```

You can also specify default configuration values in `/etc/crypter/crypter.cfg`:

```
directory=/var/run/crypter
key=/path/to/key.pem
cert=/path/to/cert.pem
```

The daemon creates two unix domain sockets: `/var/run/crypter/encrypt` and
`/var/run/crypter/decrypt` that clients can connect to and request encryption
or decryption of values. Once connected, to encrypt a value the client can
connect to the `encrypt` socket and send the value to encrypt followed by two
newlines:

```
value-to-encrypt\n
\n
```

The daemon will respond with the encrypted value in Base64 encoding, followed by
two newlines:

```
IZctKxaGojf3kQafhTwiWEeLsbizeePcdz/rFP8PFUXXKO5PrgzYHz5QKIPjjrFIR/6y1ATgXsa8
ZMvAZLNR4aEIVU2PmdSMGNf8OA+7xfzfFkuS4jVJjB7AcfJtKl1Va121uel4CizNENrCSDtSB/Dr
yV3NY6Ya/Qkkg9C1/w86MFi61M/3F8K5ifPtQmGvGNgGZ4oW6MqLda/HG14RGXGIkwEXAyfyprEc
Yd4nQgn27wyUTFfCCUEv3JIHg43Z3SAjC++QyQPrpaGvqJ8MtOjdO23kPUzMra+AMizXM5D0YwQ/
hGaCjTvrtFJi94w/7FeNcFzzD+WjtueSvDyCoQ==\n
\n
```

To decrypt, simply reverse the process - connect to the `decrypt` socket and
send the Base64-encoded encrypted value followed by two newlines.

#### Using the CLI client

A command line client is provided for use within the container that
provides a simple way to handle encryption and decryption in shell scripts:

```
crypter-client -d /var/run/crypter decrypt \
   "IZctKxaGojf3kQafhTwiWEeLsbizeePcdz/rFP8PFUXXKO5PrgzYHz5QKIPjjrFIR/6y1ATgXsa8
   ZMvAZLNR4aEIVU2PmdSMGNf8OA+7xfzfFkuS4jVJjB7AcfJtKl1Va121uel4CizNENrCSDtSB/Dr
   yV3NY6Ya/Qkkg9C1/w86MFi61M/3F8K5ifPtQmGvGNgGZ4oW6MqLda/HG14RGXGIkwEXAyfyprEc
   Yd4nQgn27wyUTFfCCUEv3JIHg43Z3SAjC++QyQPrpaGvqJ8MtOjdO23kPUzMra+AMizXM5D0YwQ/
   hGaCjTvrtFJi94w/7FeNcFzzD+WjtueSvDyCoQ=="
```

### Docker integration

To use crypter in Docker, map the host's socket directory to a volume inside
the Docker container, using a run command like:

```
$ docker run -d -v /var/run/crypter:/var/run/crypter ubuntu
```

Once running, you will see the `encrypt` and `decrypt` sockets exposed inside
the container at `/var/run/crypter`. You can now decrypt values without the
container having any knowledge of your private key.

This allows you to run both trusted and untrusted containers on your host,
and only granting trusted containers access to decryption services.
