from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

plain_password = "admin"
hashed_password = "$2b$12$Rd1KA0r.2ztHmBDWUAcx/OPnYONhrNlI6w7Lt6d1.APBVTh6xk4OO"  # Replace this with your hash

is_valid = pwd_context.verify(plain_password, hashed_password)

print("Password is valid:", is_valid)
