from datetime import timedelta
from sql_alchemy import banco
import redis



# o set é uma lista valores unicos imutaveis que não se repetem
# o blacklist sera uma instância do set
# Setup our redis connection for storing the blocklisted tokens. You will probably
# want your redis instance configured to persist data to disk, so that a restart
# does not cause your application to forget that a JWT was revoked.

ACCESS_EXPIRES = timedelta(hours=1)
REFRESH_TOKEN = timedelta(days=30)

# This could be expanded to fit the needs of your application. For example,
# it could track who revoked a JWT, when a token expires, notes for why a
# JWT was revoked, an endpoint to un-revoked a JWT, etc.


class TokenBlocklist(banco.Model):
    id = banco.Column(banco.Integer, primary_key=True)
    jti = banco.Column(banco.String(36), nullable=False, index=True)
    created_at = banco.Column(banco.DateTime, nullable=False)
