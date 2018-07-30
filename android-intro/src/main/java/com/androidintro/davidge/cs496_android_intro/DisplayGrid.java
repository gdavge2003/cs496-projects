package com.androidintro.davidge.cs496_android_intro;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.widget.TextView;

public class DisplayGrid extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.grid_view);

        //set background color
        TextView one = (TextView) findViewById(R.id.grid_1);
        TextView two = (TextView) findViewById(R.id.grid_2);
        TextView three = (TextView) findViewById(R.id.grid_3);
        TextView four = (TextView) findViewById(R.id.grid_4);
        TextView five = (TextView) findViewById(R.id.grid_5);

        one.setBackgroundColor(0xFF002857);
        two.setBackgroundColor(0xFFb3cde0);
        three.setBackgroundColor(0xFFcd6633);
        four.setBackgroundColor(0xFFe58c60);
        five.setBackgroundColor(0xFFfffd79);
    }
}