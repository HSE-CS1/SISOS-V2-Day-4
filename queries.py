from cs50 import SQL
from datetime import datetime
import pytz

# create a database object to connect to our db
db = SQL("sqlite:///signinout.db")

def get_today():
  # set the timezone to our timezone
  indytz = pytz.timezone("America/Indiana/Indianapolis")
  today = datetime.now(indytz) #get the current date and time
  cur_date = today.strftime("%m-%d-%Y") #date format 04-12-2023
  cur_time = today.strftime("%-I:%M %p") #time format 3:05 PM
  #return a dict with the current date and time
  return {'c_date':cur_date,'c_time':cur_time}


# this function will get all the passes from the database
def get_all_passes():
  sql = """
  SELECT *
    FROM passes
    ORDER BY pass_date DESC, out_time DESC
  """
  results = db.execute(sql)
  return results

# get just the passes for today
def get_todays_passes(today):
  sql = "SELECT * FROM passes WHERE pass_date = ?"
  return db.execute(sql, today)

def get_summary():
  sql = """SELECT COUNT(id) as total, f_name, l_name, student_id
  FROM passes
  GROUP BY student_id ORDER BY total DESC"""
  return db.execute(sql)
  
def get_stu_summary(stu_id):
  sql = """SELECT COUNT(id) as total, location, student_id
  FROM passes
  WHERE student_id = ?
  GROUP BY location ORDER BY total DESC"""
  return db.execute(sql, stu_id)

# this function will get the name of the student
def get_student_name(stu_id):
  sql = "SELECT f_name, l_name FROM passes WHERE student_id = ?"
  results = db.execute(sql, stu_id)[0]
  #[0] will get the first row in the list of rows
  first = results.get('f_name')
  last = results.get('l_name')
  return f"{first} {last}"
  
def get_stu_loc_summary(stu_id, loc):
  sql = """SELECT id, pass_date, out_time, in_time FROM passes
  WHERE student_id = ? AND location = ?
  ORDER BY pass_date DESC, out_time DESC"""
  return db.execute(sql, stu_id, loc)
  
def get_all_students():
  sql = """SELECT DISTINCT(student_id) as s_id, f_name, l_name 
  FROM passes
  ORDER BY l_name, f_name"""
  return db.execute(sql)


def check_for_pass(stu_id):
  # check to see if the student has any passes where they have NOT signed back in
  sql = """SELECT id FROM passes
  WHERE student_id = ? AND in_time IS NULL"""
  results =  db.execute(sql, stu_id)
  if len(results) == 0: # no student id found or no passes with empty in_time
    return 0
  elif len(results) == 1: # we found one pass that matched
    # return the id of the pass
    return results[0].get("id")
  else: # multiple passes found where the student did not sign back in
    return -1

def sign_back_in(pass_id):
  sql = """UPDATE passes SET in_time = ?
  WHERE id = ?"""
  current_time = get_today().get("c_time")
  return db.execute(sql, current_time, pass_id)
  # the update statement returns the number of rows that were updated in the table


def insert_pass(pass_data):
  # this will insert a new row in our passes table
  sql = """INSERT INTO passes
    (student_id, f_name, l_name, location, pass_date, out_time)
    VALUES
    (?, ?, ?, ?, ?, ?)
  """
  pass_id = db.execute(sql,
                      pass_data.get("stu_id"),
                      pass_data.get("first"),
                      pass_data.get("last"),
                      pass_data.get("loc"),
                      pass_data.get("pass_date"),
                      pass_data.get("out_time")
                      )
  return pass_id