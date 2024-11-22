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


class Table:
    def __init__(self, database_name, table_name):
        self.name = table_name
        self.connect = sqlite3.connect(database_name + ".db")
        self.cursor = self.connect.cursor()
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.name}(id INT PRIMARY KEY, name TEXT, age INT, is_man BIT, like_men BIT, like_women BIT, location TEXT, description TEXT, rank INT);")

    def __del__(self):
        self.connect.close()

    def save(self):
        self.connect.commit()
    
    def addProfile(self, user_id : int, name : str, age : int, is_man : bool, like_men : bool, like_women : bool, location : str, description : str, path_to_photo : str) -> bool:
        try:
            self.cursor.execute(f"INSERT INTO {self.name} VALUES ({user_id}, '{name}', {age}, {int(is_man)}, {int(like_men)}, {int(like_women)}, '{location}', '{description}', NULL, 1, {path_to_photo});")
            return True
        except:
            return False
    
    def createEmptyProfileById(self, user_id : int):
        self.addProfile(user_id, "", 0, False, False, False, "", "", "none")
    
    def getProfileById(self, user_id : int) -> list:
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE id = {user_id};")
        try:
            return self.cursor.fetchall()[0]
        except:
            return []
    
    def getProfiles(self) -> list:
        self.cursor.execute(f"SELECT * FROM {self.name};")
        return self.cursor.fetchall()
    
    def getProfilesByPreferences(self, is_man : bool, like_men : bool, like_women : bool) -> list:
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE (((like_men = 1) AND (like_men = {int(is_man)})) OR ((like_women = 1) AND (like_women = {int(not is_man)}))) AND (is_man = {int(like_men)} OR is_man = {int(not like_women)});")
        return self.cursor.fetchall()
    
    def getProfilesByPreferencesWithLocation(self, location : str, is_man : bool, like_men : bool, like_women : bool) -> list:
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE location = '{location}' AND (((like_men = 1) AND (like_men = {int(is_man)})) OR ((like_women = 1) AND (like_women = {int(not is_man)}))) AND (is_man = {int(like_men)} OR is_man = {int(not like_women)});")
        return self.cursor.fetchall()
    
    def getRandomProfile(self, profiles : list) -> list:
        profiles_count = len(profiles)
        ranks = [profiles[i][8] for i in range(profiles_count)]
        intervals = [sum(ranks[ : i]) for i in range(1, profiles_count + 1)]
        random_value = random.randint(1, intervals[-1])
        current_interval = 0
        while (random_value > intervals[current_interval]):
            current_interval += 1
        return profiles[current_interval]
    
    def getRandomProfileByPreferences(self, self_id : int, is_man : bool, like_men : bool, like_women : bool) -> list:
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE id != {self_id} AND (((like_men = 1) AND (like_men = {int(is_man)})) OR ((like_women = 1) AND (like_women = {int(not is_man)}))) AND (is_man = {int(like_men)} OR is_man = {int(not like_women)}) ORDER BY rank;")
        return self.getRandomProfile(self.cursor.fetchall())
    
    def getRandomProfileByPreferencesWithLocation(self, self_id : int, location : str, is_man : bool, like_men : bool, like_women : bool) -> list:
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE id != {self_id} AND location = '{location}' AND (((like_men = 1) AND (like_men = {int(is_man)})) OR ((like_women = 1) AND (like_women = {int(not is_man)}))) AND (is_man = {int(like_men)} OR is_man = {int(not like_women)}) ORDER BY rank;")
        return self.getRandomProfile(self.cursor.fetchall())
    
    def getRankById(self, user_id : int) -> int:
        self.cursor.execute(f"SELECT rank FROM {self.name} WHERE id = {user_id};")
        return self.cursor.fetchall()[0][0]
    
    def editPhotoById(self, user_id : int, new_photo : str):
        self.cursor.execute(f"UPDATE {self.name} SET photo = '{new_photo}' WHERE id = {user_id};")
    
    def editNameById(self, user_id : int, new_name : str):
        self.cursor.execute(f"UPDATE {self.name} SET name = '{new_name}' WHERE id = {user_id};")
    
    def editAgeById(self, user_id : int, new_age : int):
        self.cursor.execute(f"UPDATE {self.name} SET age = {new_age} WHERE id = {user_id};")
    
    def editGenderById(self, user_id : int, new_flag : bool):
        self.cursor.execute(f"UPDATE {self.name} SET is_man = {int(new_flag)} WHERE id = {user_id};")
    
    def editGenderPreferencesById(self, user_id : int, new_men_flag : bool, new_women_flag : bool):
        self.cursor.execute(f"UPDATE {self.name} SET like_men = {int(new_men_flag)}, like_women = {int(new_women_flag)} WHERE id = {user_id};")
    
    def editLocationById(self, user_id : int, new_location : str):
        self.cursor.execute(f"UPDATE {self.name} SET location = '{new_location}' WHERE id = {user_id};")
    
    def editDescriptionById(self, user_id : int, new_description : str):
        self.cursor.execute(f"UPDATE {self.name} SET description = '{new_description}' WHERE id = {user_id};")
    
    def upRankById(self, user_id : int):
        self.cursor.execute(f"UPDATE {self.name} SET rank = (rank + 1) WHERE id = {user_id};")
    
    def downRankById(self, user_id : int):
        if (self.getRankById(user_id) > 1):
            self.cursor.execute(f"UPDATE {self.name} SET rank = (rank - 1) WHERE id = {user_id};")
            return True
        return False
    
    def clear(self):
        self.cursor.execute(f"DELETE FROM {self.name};") 