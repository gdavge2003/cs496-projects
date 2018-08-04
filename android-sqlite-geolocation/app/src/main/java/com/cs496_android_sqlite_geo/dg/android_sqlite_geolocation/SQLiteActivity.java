package com.cs496_android_sqlite_geo.dg.android_sqlite_geolocation;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.os.Bundle;
import android.provider.BaseColumns;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.SimpleCursorAdapter;


public class SQLiteActivity extends AppCompatActivity{
    SQLiteInstance mySQLiteInstance;
    SQLiteDatabase mySQLiteDB;
    Cursor mySQLiteCursor;
    SimpleCursorAdapter mySQLiteCursorAdapter;
    Button mySubmitButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // creates a new db instance in this context, then gets pointer to the db
        mySQLiteInstance = new SQLiteInstance(this);
        mySQLiteDB = mySQLiteInstance.getWritableDatabase();

        // sets up the button in the view to submit data
        mySubmitButton = (Button) findViewById(R.id.sql_add_row_button);
        mySubmitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // submits string, long/lat information if db is available
                if (mySQLiteDB != null) {
                    ContentValues vals = new ContentValues();
                    vals.put(DBContract.AppTable.COLUMN_NAME_STRING,
                            ((EditText) findViewById(R.id.inputString)).getText().toString());
                    vals.put(DBContract.AppTable.COLUMN_NAME_LATITUDE, 23.42);
                    vals.put(DBContract.AppTable.COLUMN_NAME_LONGITUDE, 18.42);

                    // insert into table
                    mySQLiteDB.insert(DBContract.AppTable.TABLE_NAME, null, vals);

                    // update rows in UI
                    displayTable();
                }
                else {
                    Log.d("SQLActivity", "Unable to access database for writing.");
                }
            }
        });
    }

    private void displayTable() {
        if (mySQLiteDB != null) {
            try {




            } catch (Exception e) {
                Log.d("SQLActivity", "Error accessing and loading from database.");
            }
        }
    }
}

// New instances to setup db and table
class SQLiteInstance extends SQLiteOpenHelper {
    public SQLiteInstance(Context context) {
        // creates the db with given name and version
        super(context, DBContract.AppTable.DB_NAME, null, DBContract.AppTable.DB_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        // creates table in initialized db
        db.execSQL(DBContract.AppTable.SQL_CREATE_TABLE);

        // insert initial values as test
//        ContentValues testValues = new ContentValues();
//        testValues.put(DBContract.AppTable.COLUMN_NAME_STRING, "Test");
//        testValues.put(DBContract.AppTable.COLUMN_NAME_LATITUDE, 43.237);
//        testValues.put(DBContract.AppTable.COLUMN_NAME_LONGITUDE, 32.237);
//        db.insert(DBContract.AppTable.TABLE_NAME,null, testValues);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL(DBContract.AppTable.SQL_DROP_DEMO_TABLE);
        onCreate(db);
    }

}

// final constants for db and table details
final class DBContract {
    private DBContract() {};

    public final class AppTable implements BaseColumns {
        public static final String DB_NAME = "app_db";
        public static final String TABLE_NAME = "string_geolocation_data";
        public static final String COLUMN_NAME_STRING = "input_string";
        public static final String COLUMN_NAME_LONGITUDE = "longitude";
        public static final String COLUMN_NAME_LATITUDE = "latitude";
        public static final int DB_VERSION = 1;

        public static final String SQL_CREATE_TABLE = "CREATE TABLE " +
                AppTable.TABLE_NAME + "(" + AppTable._ID + " INTEGER PRIMARY KEY NOT NULL," +
                AppTable.COLUMN_NAME_STRING + " VARCHAR(255)," +
                AppTable.COLUMN_NAME_LATITUDE + " REAL," +
                AppTable.COLUMN_NAME_LONGITUDE + " REAL);";

        public static final String SQL_DROP_DEMO_TABLE = "DROP TABLE IF EXISTS " + AppTable.TABLE_NAME;
    }
}