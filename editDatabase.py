from database import Database

class CRUD(Database):
    def __init__(self) -> None:
        super().__init__()
    
    def insertDB(self,schema,table,colum,data):
        """DB에 Data를 넣는 함수입니다.

        Args:
            schema (_type_): Data를 넣을 Schema를 지정합니다
            table (_type_): Data를 넣을 Table을 지정합니다
            colum (_type_): Data를 넣을 Colum을 지정합니다
            data (_type_): 입력할 Data를 씁니다
        """
        if(colum == None):
            sql = " INSERT INTO {schema}.{table} VALUES {data} ;".format(schema=schema,table=table,colum=colum,data=data)
        else:
            sql = " INSERT INTO {schema}.{table}({colum}) VALUES {data} ;".format(schema=schema,table=table,colum=colum,data=data)
            
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e :
            self.db.rollback()
            print("Database read error:", e)
            print(" insert DB err ",e) 
    
    def readDB(self,schema,table,colum,condition):
        """DB에 있는 Data를 받아오는 함수입니다

        Args:
            schema (_type_): Data를 넣을 Schema를 지정합니다
            table (_type_): Data를 넣을 Table을 지정합니다
            colum (_type_): Data를 넣을 Colum을 지정합니다
            data (_type_): 입력할 Data를 씁니다
            condition (_type_): 조건을 지정합니다 postsql의 조건문을 이용합니다.
            
        Returns:
            _type_: Data를 가져옵니다.
        """
        if(condition == None):
            sql = " SELECT {colum} from {schema}.{table}".format(colum=colum,schema=schema,table=table)
        else:
            sql = " SELECT {colum} from {schema}.{table} WHERE {condition}".format(colum=colum,schema=schema,table=table,condition=condition)
            
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e :
            self.db.rollback()
            print("Database read error:", e)
            result = (" read DB err",e)
        
        return result

    def updateDB(self,schema,table,colum,value,condition):
        """ Data의 값을 바꾸는 함수입니다.

        Args:
            schema (_type_): Data를 넣을 Schema를 지정합니다
            table (_type_): Data를 넣을 Table을 지정합니다
            colum (_type_): Data를 넣을 Colum을 지정합니다
            data (_type_): 입력할 Data를 씁니다
            condition (_type_): 조건을 지정합니다 postsql의 조건문을 이용합니다.
            value (_type_): 바꿀값을 입력합니다.
        """
        sql = " UPDATE {schema}.{table} SET {colum}='{value}' WHERE {condition} ".format(schema=schema
        , table=table , colum=colum ,value=value,condition=condition )
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e :
            self.db.rollback()
            print("Database read error:", e)
            print(" update DB err",e)

    def deleteDB(self,schema,table,condition):
        """DB에 Data를 삭제하는 함수입니다.

        Args:
            schema (_type_): 삭제할 Schema를 지정합니다
            table (_type_): 삭제할 Table을 지정합니다
            colum (_type_): 삭제할 Colum을 지정합니다
            condition (_type_): 조건을 지정합니다 postsql의 조건문을 이용합니다.
            
        Returns:
            _type_: 에러가 있는지 출력합니다
        """
        
        sql = " delete from {schema}.{table} where {condition} ; ".format(schema=schema,table=table,
        condition=condition)
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print("Database read error:", e)
            print( "delete DB err", e)