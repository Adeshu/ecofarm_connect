-- SQL script to add video_file column to courses_lesson table
-- Run this directly in your MySQL database if migration doesn't work

ALTER TABLE courses_lesson 
ADD COLUMN video_file VARCHAR(100) NULL 
AFTER video_url;

