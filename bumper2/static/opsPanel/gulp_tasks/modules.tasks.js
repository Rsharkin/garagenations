"use strict";

var gulp = require('gulp'),
    concat = require('gulp-concat'),
    cssnano = require('gulp-cssnano'),
    pump = require('pump'),
    uglify = require('gulp-uglify'),
    gulpif = require('gulp-if'),
    replace = require('gulp-batch-replace'),
    livereload = require('gulp-livereload'),
    del = require('del'),

    production = (process.argv.indexOf('--production') !== -1),
    staging = (process.argv.indexOf('--staging') !== -1),
    jsSrcDir,
    jsVendorSrcDir,
    cssSrcDir,
    imgSrcDir,
    htmlSrcDir,
    pageSrcDir,
    firebasePath,
    baseDir = './',
    output = './gulp_build/',
    replaceList;


const jshint = require('gulp-jshint');
const stylish = require('jshint-stylish');

replaceList =
    require('../gulp_config/' + (production ? 'production' : staging ? 'staging' : 'local') + '.js');

jsSrcDir = [baseDir + "opsApp/app.js", baseDir + "opsApp/config.js", baseDir + "opsApp/directives.js",
    baseDir + "opsApp/main-controller.js", baseDir + "opsApp/services/*.js", baseDir + "opsApp/core/**/*.js"];

jsVendorSrcDir = [
    baseDir + "js/*.js",
    baseDir + "js/vendor/*.js"
];

cssSrcDir = [baseDir + "css/**/*.css"];
imgSrcDir = [baseDir + "img/**"];
htmlSrcDir = [baseDir + "opsApp/views/**/*.html"];

pageSrcDir = '../../templates/ops-panel/index.html';
firebasePath = [baseDir+  'opsApp/firebase/**'];

gulp.task('Clean_PublicFolder', function () {
  return del([
    'public/**/*'
  ]);
});

gulp.task('Compile_Styles', ['Clean_PublicFolder'], function () {
    return gulp.src(cssSrcDir)
        .pipe(gulpif(production, cssnano()))
        .pipe(gulp.dest((output) + 'css'));
});

gulp.task('Concat_vendor_JS', ['Clean_PublicFolder'], function() {
    return gulp.src(jsVendorSrcDir)
        .pipe(concat('vendor.min.js', {newLine: ';'}))
        .pipe(gulp.dest((output) + 'js'));
});

gulp.task('Compile_vendor_JS', ['Concat_vendor_JS'], function(cb) {
    var options = {
        mangle: false
    };
    pump([
            gulp.src((output) + 'js/vendor.min.js'),
            uglify(options),
            gulp.dest((output) + 'js')
        ],
        cb
    );
});

gulp.task('lint', function() {
  return gulp.src(jsSrcDir)
    .pipe(jshint())
    .pipe(jshint.reporter(stylish))
    .pipe(jshint.reporter('fail'));
});

gulp.task('Concat_Bumper_JS', ['Clean_PublicFolder', 'lint'], function() {
    return gulp.src(jsSrcDir)
        .pipe(concat('bumper.min.js', {newLine: ';'}))
        .pipe(gulp.dest((output) + 'js'));
});

gulp.task('Compile_Bumper_JS', ['Concat_Bumper_JS'], function(cb) {
    var options = {
        mangle: false
    };
    pump([
            gulp.src((output) + 'js/bumper.min.js'),
            uglify(options),
            gulp.dest((output) + 'js')
        ],
        cb
    );
});

gulp.task('Copy_Img', ['Clean_PublicFolder'], function () {
    return gulp.src(imgSrcDir)
        .pipe(gulp.dest((output) + 'img'));
});

gulp.task('Copy_Firebase', ['Clean_PublicFolder'], function () {
    return gulp.src(firebasePath)
        .pipe(gulp.dest((output) + 'firebase'));
});

gulp.task('Compile_Home_Page',['Clean_PublicFolder'], function () {
    return gulp.src(pageSrcDir)
        .pipe(replace(replaceList))
        .pipe(gulp.dest('./public'));
});

gulp.task('Compile_Views', ['Clean_PublicFolder'], function () {
    // to compress and replace if required.
    return gulp.src(htmlSrcDir)
        .pipe(replace(replaceList))
        .pipe(gulp.dest((output) + 'views'));
});

gulp.task('Increase_Version_JS', ['Compile_Bumper_JS'], function () {
    return gulp.src((output) + 'js/bumper.min.js')
        .pipe(replace(replaceList))
        .pipe(gulp.dest((output) + 'js'));
});

