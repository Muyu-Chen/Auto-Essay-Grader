from modifyUsers import hashPassword

newpw = "12345678"
creating_date = "20241213"
creating_time = "235959"

newHashedPW=hashPassword(newpw, creating_date, creating_time)
print("New hashed password: ", newHashedPW)
