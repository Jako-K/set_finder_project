// Copyright (c) 2020 Facebook, Inc. and its affiliates.
// All rights reserved.
//
// This source code is licensed under the BSD-style license found in the
// LICENSE file in the root directory of this source tree.

package org.pytorch.demo.objectdetection;

import android.annotation.SuppressLint;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;


public class ResultView extends View {

    private final static int SQUARE_SIZE = 20;

    private Paint mPaintRectangle;
    private Paint mPaintText;
    private ArrayList<Result> mResults;
    private int number_of_cards_detected;

    public ResultView(Context context) {
        super(context);
    }

    public ResultView(Context context, AttributeSet attrs){
        super(context, attrs);
        mPaintRectangle = new Paint();
        mPaintRectangle.setColor(Color.YELLOW);
        mPaintText = new Paint();
    }

    ///////////////////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////     MINE START       ///////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////

    public static boolean is_a_valid_set_solution(int[] combination){
        String c1 = PrePostProcessor.mClasses[combination[0]];
        String c2 = PrePostProcessor.mClasses[combination[1]];
        String c3 = PrePostProcessor.mClasses[combination[2]];

        char c1_color = c1.charAt(0);
        char c1_count = c1.charAt(1);
        char c1_shape = c1.charAt(2);
        char c1_fill  = c1.charAt(3);

        char c2_color = c2.charAt(0);
        char c2_count = c2.charAt(1);
        char c2_shape = c2.charAt(2);
        char c2_fill  = c2.charAt(3);

        char c3_color = c3.charAt(0);
        char c3_count = c3.charAt(1);
        char c3_shape = c3.charAt(2);
        char c3_fill  = c3.charAt(3);

        if ( (c1.equals(c2)) || (c2.equals(c3)) || (c1.equals(c3)) ) {return false;}

        // all these booleans could be simplified, but I have kept it like this because it's more intuitive.
        boolean all_same_color = (c1_color == c2_color) && (c2_color == c3_color) && (c1_color == c3_color);
        boolean all_different_color = (c1_color != c2_color) && (c2_color != c3_color) && (c1_color != c3_color);

        boolean all_same_count = (c1_count == c2_count) && (c2_count == c3_count) && (c1_count == c3_count);
        boolean all_different_count = (c1_count != c2_count) && (c2_count != c3_count) && (c1_count != c3_count);

        boolean all_same_shape = (c1_shape == c2_shape) && (c2_shape == c3_shape) && (c1_shape == c3_shape);
        boolean all_different_shape = (c1_shape != c2_shape) && (c2_shape != c3_shape) && (c1_shape != c3_shape);

        boolean all_same_fill = (c1_fill == c2_fill) && (c2_fill == c3_fill) && (c1_fill == c3_fill);
        boolean all_different_fill = (c1_fill != c2_fill) && (c2_fill != c3_fill) && (c1_fill != c3_fill);

        if ( !(all_same_color || all_different_color) ) {return false;}
        if ( !(all_same_shape || all_different_shape) ) {return false;}
        if ( !(all_same_count || all_different_count) ) {return false;}
        if ( !(all_same_fill  || all_different_fill)  ) {return false;}

        return true;
    }


    public static int[][] get_all_legal_solution(int[] pool){
        int n = pool.length;
        int[] indices = new int[]{0,1,2};
        int[] temp = new int[3];
        int all_solution_i = 0;

        // Setup all_solutions array and fill it with -1
        int[][] all_solutions = new int[15][3]; // Never gonna find more than 15.
        for (int[] all_solution : all_solutions) {
            Arrays.fill(all_solution, -1);
        }
        if (3 > n) return all_solutions;

        // Check the very first solution i think.
        for (int i = 0; i < 3; i++){
            temp[i] = pool[indices[i]];
        }
        if (is_a_valid_set_solution(temp)){
            for(int k=0; k<3; k++){
                all_solutions[all_solution_i][k] = temp[k];
            }
            Log.d("Is_valid" + String.valueOf(all_solution_i), Arrays.toString(temp) + Arrays.toString(all_solutions[all_solution_i]));
            all_solution_i++;
        }

        while ( true ){

            int I = -1;
            for (int i = 2; i >= 0; i--){
                if ( indices[i] != (i + n - 3) ) {I = i; break;}
            }
            if (I == -1){return all_solutions;}

            indices[I] += 1;
            for (int j=I+1; j<3; j++){ indices[j] = indices[j - 1] + 1;}

            for (int i = 0; i < 3; i++){ temp[i] = pool[indices[i]]; }
            if (is_a_valid_set_solution(temp)){
                for(int k=0; k<3; k++){
                    all_solutions[all_solution_i][k] = temp[k];
                }
                all_solution_i++;
            }
        }
    }


    public static boolean is_in_solution(int[] solution, int card){
        for (int s_card: solution) {
            if (s_card == card) {return true;}
        }
        return false;
    }


    @SuppressLint("DrawAllocation")
    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if ( number_of_cards_detected == 0) return;

        // Init stuff
        String[] colors = {"#1f77b4" , "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#e348f8", "#a4b503", "#94955b"};
        String[] card_string_solutions = new String[number_of_cards_detected];
        int counter = 0;
        int solution_i = 0;
        int result_i = 0;


        // Make a list of all detected cards
        int[] cards = new int[number_of_cards_detected];
        for (Result result : mResults) {
            cards[counter] = result.classIndex;
            counter++;
        }


        // Find all possible sets from the detected cards
        int[][] all_solutions = get_all_legal_solution((cards));


        // Draw white line around all detected cards
        for (Result result : mResults) {
            card_string_solutions[result_i] = "";
            mPaintRectangle.setStrokeWidth(1);
            mPaintRectangle.setStyle(Paint.Style.STROKE);
            mPaintRectangle.setColor(Color.WHITE);
            canvas.drawRect(result.rect, mPaintRectangle);
            result_i++;
        }

        // Make solution string for display
        for (int[] solution_found : all_solutions) {
            result_i = 0;
            for (Result result : mResults) {
                if (is_in_solution(solution_found, result.classIndex)) {
                    card_string_solutions[result_i] += String.valueOf(solution_i) + " ";
                }
                result_i++;
            }
            solution_i++;
        }

        // Draw squares according to which solution a particular cards occurs in.
        String result_string;
        for (int square_index=0; square_index<all_solutions.length; square_index++){
            result_i = 0;
            for (Result result : mResults) {
                result_string = card_string_solutions[result_i];
                if (!result_string.equals("") && result_string.contains(String.valueOf(square_index))) {
                    Path mPath = new Path();
                    RectF mRectF = new RectF(
                            result.rect.left + SQUARE_SIZE * (square_index),
                            result.rect.top,
                            result.rect.left + SQUARE_SIZE * (square_index + 1),
                            result.rect.top + SQUARE_SIZE);
                    mPath.addRect(mRectF, Path.Direction.CW);

                    mPaintText.setColor(Color.parseColor(colors[square_index]));
                    canvas.drawPath(mPath, mPaintText);
                }
            result_i++;
            }
        }
    }


    public void setResults(ArrayList<Result> results) {
        number_of_cards_detected = results.size();
        if (number_of_cards_detected < 2){
            mResults = results;
            return;
        }

        // Order the results from left to right and top to bottom.
        // My hope is that this will lead to a more stable display i.e.
        // The colored solution squares stay the same and don't change
        // every order frame.

        int[] order_metrics = new int[number_of_cards_detected];
        Map<Integer, Integer> metric_to_index = new HashMap<Integer, Integer>();
        ArrayList<Result> ordered_results = new ArrayList<Result>(number_of_cards_detected);

        for (int i=0; i<number_of_cards_detected; i++){
            order_metrics[i] = results.get(i).rect.left + results.get(i).rect.top;
            metric_to_index.put(order_metrics[i], i);
        }
        Arrays.sort(order_metrics);

        int result_i = 0;
        for (int i=0; i<number_of_cards_detected; i++){
            result_i = metric_to_index.get(order_metrics[i]);
            ordered_results.add(i, results.get(result_i));
        }
        mResults = ordered_results;
    }
}


///////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////     MINE END     ///////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////