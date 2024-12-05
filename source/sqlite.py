import sqlite3
import random


class Database:
    def __init__(self, database_name: str):
        self.connect(database_name)
    
    def __del__(self):
        self.connect.close()
    
    def connect(self, database_name: str):
        self.connect = sqlite3.connect(database_name + ".db", check_same_thread=False)
        self.cursor = self.connect.cursor()

    def save(self):
        self.connect.commit()
    
    def addProfile(self, user_id: int):
        try:
            self.cursor.execute(f"INSERT INTO profiles (user_id) VALUES ({user_id});")
        except:
            pass
    
    def updateUsername(self, user_id: int, username: str):
        self.cursor.execute(f"UPDATE profiles SET username = '{username}' WHERE user_id = {user_id};")
    
    def getUser(self, user_id: int):
        self.cursor.execute(f"SELECT * FROM profiles WHERE user_id = {user_id};")
        try:
            return self.cursor.fetchall()[0]
        except:
            return None
    
    def getLabel(self, label_name: str):
        self.cursor.execute(f"SELECT value FROM labels WHERE label_name = '{label_name}';")
        try:
            return self.cursor.fetchall()[0][0]
        except:
            return []
    
    def getQuestionText(self, id: int):
        self.cursor.execute(f"SELECT question FROM test_questions WHERE id = {id};")
        try:
            return self.cursor.fetchall()[0][0]
        except:
            return []
    
    def getQuestionAnswers(self, id: int):
        self.cursor.execute(f"SELECT answer_id, text FROM test_answers WHERE question_id = {id};")
        try:
            return self.cursor.fetchall()
        except:
            return []
    
    def getQuestionAnswer(self, question_id: int, answer_id: int):
        self.cursor.execute(f"SELECT * FROM test_answers WHERE question_id = {question_id} AND answer_id = {answer_id};")
        try:
            return self.cursor.fetchall()[0]
        except:
            return []
    
    def setTestResult(self, user_id: int, result: str):
        try:
            self.cursor.execute(f"UPDATE profiles SET test_result = '{result}' WHERE user_id = {user_id};")
        except:
            pass
    
    def getTestResult(self, user_id: int):
        self.cursor.execute(f"SELECT test_result FROM profiles WHERE user_id = {user_id};")
        try:
            return self.cursor.fetchall()[0][0]
        except:
            return []
    
    def getPositionById(self, position_id: int):
        self.cursor.execute(f"SELECT * FROM positions WHERE id = {position_id};")
        try:
            return self.cursor.fetchall()[0]
        except:
            return []
    
    def getCategoryById(self, category_id: int):
        self.cursor.execute(f"SELECT * FROM categories WHERE id = {category_id};")
        try:
            return self.cursor.fetchall()[0]
        except:
            return []
    
    def getSubcategoryById(self, subcategory_id: int):
        self.cursor.execute(f"SELECT * FROM subcategories WHERE id = {subcategory_id};")
        try:
            return self.cursor.fetchall()[0]
        except:
            return []
    
    def getPositionsCategories(self):
        self.cursor.execute(f"SELECT id, name FROM categories;")
        try:
            return self.cursor.fetchall()
        except:
            return []
    
    def getPositionsSubcategories(self, category_id: int):
        self.cursor.execute(f"SELECT id, name FROM subcategories WHERE category_id = {category_id};")
        try:
            return self.cursor.fetchall()
        except:
            return []
    
    def getPositions(self, subcategory_id: str):
        self.cursor.execute(f"SELECT id, name FROM positions WHERE subcategory_id = {subcategory_id};")
        try:
            return self.cursor.fetchall()
        except:
            return []
        

def getConnection():
    return Database("beauty_database")