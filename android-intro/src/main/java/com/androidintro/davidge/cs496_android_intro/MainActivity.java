package com.androidintro.davidge.cs496_android_intro;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.RelativeLayout;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //1. list horizontally view of numbers 1-5
        Button textHorizontal = (Button) findViewById(R.id.horizontal_view);
        textHorizontal.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, DisplayHorizontal.class);
                startActivity(intent);
            }
        });

        //2. list vertically view of numbers 1-5
        Button textVertical = (Button) findViewById(R.id.vertical_view);
        textVertical.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, DisplayVertical.class);
                startActivity(intent);
            }
        });

        //3. grid view of numbers 1-5
        Button textGrid = (Button) findViewById(R.id.grid_view);
        textGrid.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, DisplayGrid.class);
                startActivity(intent);
            }
        });

        //4. relative "waterfall" view of numbers 1-5
        Button relativeGrid = (Button) findViewById(R.id.relative_view);
        relativeGrid.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, DisplayRelative.class);
                startActivity(intent);
            }
        });

    }
}
