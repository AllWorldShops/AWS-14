from odoo import api, fields, models, _
import mysql.connector
from odoo import  exceptions
from odoo.exceptions import ValidationError

class MysqldbConfig(models.Model):
    _name = 'mysqldb.config'
    _description = 'MySQL DB Configuration'
    _rec_name ='db_username'
    _inherit = ['mail.thread']

    db_provider_name=fields.Selection([('mysql', "MySQL"),('mssql', "MSSQL")], default="mysql",string='Database Provider')
    db_hostname=fields.Char(string='IP Address of Host',required=True)
    db_name=fields.Char(string='Database Name',required=True)
    db_username=fields.Char(string='User Name',required=True)
    db_password=fields.Char(string='Password',required=True)
    db_sync_type=fields.Selection([('tly2odo', "Tally.ERP 9 to Odoo"),('odo2tly', "Odoo to Tally.ERP 9"),('odotly', "Bi-Directional")],string='Type of Sync',required=True)
    db_test_query=fields.Text(string='Run Test Connection',required=True)
    db_query_result=fields.Text(string='Result Connection', readonly=True, track_visibility='onchange')

    # @api.multi
    def run_testquery(self):
        print("hi this is test")
        try:
            con=mysql.connector.connect(host=self.db_hostname,database=self.db_name,user=self.db_username,password=self.db_password)
            #(host='10.10.30.91',database='tallydata_01_12',user='francies',password='Ppts@123')
            cursor=con.cursor()
            cursor.execute(self.db_test_query)
            recordss=cursor.fetchall()
            self.db_query_result=recordss
            print("records",recordss)
            con.close()
            cursor.close()

        except Exception as e:
            print("Error reading data from MySQL table", e)
            raise ValidationError(_('Error reading data from MySQL table'))
            raise exceptions.Warning('Warning message')

        finally:
            con = mysql.connector.connect(host=self.db_hostname, database=self.db_name, user=self.db_username,
                                          password=self.db_password)
            if (con.is_connected()):
                con.close()
                cursor.close()
                print("MySQL connection is closed")