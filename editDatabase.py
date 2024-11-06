from database import Database

class CRUD(Database):
    def __init__(self) -> None:
        super().__init__()
        
    def insertDB(self,schema,table,colum,data):
        if(colum == None):
            sql = " INSERT INTO {schema}.{table} VALUES {data} ;".format(schema=schema,table=table,colum=colum,data=data)
        else:
            sql = " INSERT INTO {schema}.{table}({colum}) VALUES {data} ;".format(schema=schema,table=table,colum=colum,data=data)
            
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e :
            print(" insert DB err ",e) 
    
    def readDB(self,schema,table,colum,condition):
        if(condition == None):
            sql = " SELECT {colum} from {schema}.{table}".format(colum=colum,schema=schema,table=table)
        else:
            sql = " SELECT {colum} from {schema}.{table} WHERE {condition}".format(colum=colum,schema=schema,table=table,condition=condition)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e :
            result = (" read DB err",e)
        
        return result

    def updateDB(self,schema,table,colum,value,condition):
        sql = " UPDATE {schema}.{table} SET {colum}='{value}' WHERE {condition} ".format(schema=schema
        , table=table , colum=colum ,value=value,condition=condition )
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e :
            print(" update DB err",e)

    def deleteDB(self,schema,table,condition):
        sql = " delete from {schema}.{table} where {condition} ; ".format(schema=schema,table=table,
        condition=condition)
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print( "delete DB err", e)