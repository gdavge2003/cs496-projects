package com.cs496_android_sqlite_geo.dg.android_sqlite_geolocation;

import android.app.Dialog;
import android.content.ContentValues;
import android.content.Context;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.location.Location;
import android.os.Bundle;
import android.provider.BaseColumns;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.SimpleCursorAdapter;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GoogleApiAvailability;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.location.LocationListener;

public class MainActivity extends AppCompatActivity implements
        GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener{

    // database variables
    SQLiteInstance mySQLiteInstance;
    SQLiteDatabase mySQLiteDB;
    Cursor mySQLiteCursor;
    SimpleCursorAdapter mySQLiteCursorAdapter;
    Button mySubmitButton, myDeleteButton;

    // geolocation variables
    GoogleApiClient myApiClient;
    LocationRequest myLocationReq;
    Location myLastLocation;
    LocationListener myLocationListener;
    String latitude, longitude;

    // geolocation/permission constants
    static final int LOCATION_PERMISSON_RESULT = 17;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // setup google api client
        if (myApiClient == null) {
            myApiClient = new GoogleApiClient.Builder(this)
                    .addConnectionCallbacks(this)
                    .addOnConnectionFailedListener(this)
                    .addApi(LocationServices.API)
                    .build();
        }

        // get current location coordinates constantly otherwise default to set standard
        myLocationReq = LocationRequest.create();
        myLocationReq.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
        myLocationReq.setInterval(5000);
        myLocationReq.setFastestInterval(5000);

        // set up location listener
        myLocationListener = new LocationListener() {
            @Override
            public void onLocationChanged(Location location) {
                if (location != null) {
                    latitude = String.valueOf(location.getLatitude());
                    longitude = String.valueOf(location.getLongitude());
                } else { // set default to OSU
                    latitude = "44.5 (default)";
                    longitude = "-123.2 (default)";
                }
            }
        };

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
                    vals.put(DBContract.AppTable.COLUMN_NAME_LATITUDE, latitude);
                    vals.put(DBContract.AppTable.COLUMN_NAME_LONGITUDE, longitude);

                    // insert into table
                    mySQLiteDB.insert(DBContract.AppTable.TABLE_NAME, null, vals);

                    // clears up the user text submit field
                    ((EditText) findViewById(R.id.inputString)).setText("");

                    // update rows in UI
                    displayTable();
                }
                else {
                    Log.d("SQLActivity", "Unable to access database for writing.");
                }
            }
        });

        // debugging only (sets button to wipe table contents)
        myDeleteButton = (Button) findViewById(R.id.delete_table_contents);
        myDeleteButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (mySQLiteDB != null) {
                    mySQLiteDB.execSQL(DBContract.AppTable.SQL_DROP_DEMO_TABLE);
                    mySQLiteDB.execSQL(DBContract.AppTable.SQL_CREATE_TABLE);

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
                // clear out previous cursorAdapter contents
                if (mySQLiteCursorAdapter != null && mySQLiteCursorAdapter.getCursor() != null) {
                    if(!mySQLiteCursorAdapter.getCursor().isClosed())
                        mySQLiteCursorAdapter.getCursor().close();
                }

                // create cursor to point at results
                mySQLiteCursor = mySQLiteDB.query(DBContract.AppTable.TABLE_NAME,
                        new String[]{DBContract.AppTable._ID,
                            DBContract.AppTable.COLUMN_NAME_STRING,
                                DBContract.AppTable.COLUMN_NAME_LATITUDE,
                                DBContract.AppTable.COLUMN_NAME_LONGITUDE},
                        null, null, null, null, null);

                Log.d("SQLActivity", DatabaseUtils.dumpCursorToString(mySQLiteCursor));

                // setup cursor adapter
                ListView mainListView = (ListView) findViewById(R.id.sql_show_rows);
                mySQLiteCursorAdapter = new SimpleCursorAdapter(this,
                        R.layout.single_row,
                        mySQLiteCursor,
                        new String[]{DBContract.AppTable.COLUMN_NAME_STRING, DBContract.AppTable.COLUMN_NAME_LATITUDE, DBContract.AppTable.COLUMN_NAME_LONGITUDE},
                        new int[]{R.id.sql_single_row_string, R.id.sql_single_row_lat, R.id.sql_single_row_long}, 0);

                // set adapter to the row
                mainListView.setAdapter(mySQLiteCursorAdapter);
            } catch (Exception e) {
                Log.d("SQLActivity", "Error accessing and loading from database. Error: " + e);
            }
        }
    }

    // set of overriden geolocation/permission methods needed for geolocation services
    @Override
    protected void onStart() {
        myApiClient.connect();
        super.onStart();
    }

    @Override
    protected void onStop() {
        myApiClient.disconnect();
        super.onStop();
    }

    @Override
    public void onConnectionSuspended(int i) {}

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {
        Dialog errDialog = GoogleApiAvailability.getInstance().getErrorDialog(this, connectionResult.getErrorCode(), 0);
        errDialog.show();
        return;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults){
        if(requestCode == LOCATION_PERMISSON_RESULT){
            if(grantResults.length > 0){
                updateLocation();
            }
        }
    }

    @Override
    public void onConnected(@Nullable Bundle bundle) {
        if (ActivityCompat.checkSelfPermission(this,
                android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION, android.Manifest.permission.ACCESS_COARSE_LOCATION}, LOCATION_PERMISSON_RESULT);
            latitude = "44.5";
            longitude = "-123.2";

            return;
        }

        updateLocation();
    }

    // update location after permission passes
    private void updateLocation() {
        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED
                && ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            return;
        }

        //myLastLocation = LocationServices.FusedLocationApi.getLastLocation(myApiClient);

        LocationServices.FusedLocationApi.requestLocationUpdates(myApiClient, myLocationReq, myLocationListener);
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
                AppTable.COLUMN_NAME_LATITUDE + " VARCHAR(255)," +
                AppTable.COLUMN_NAME_LONGITUDE + " VARCHAR(255));";

        public static final String SQL_DROP_DEMO_TABLE = "DROP TABLE IF EXISTS " + AppTable.TABLE_NAME;
    }
}