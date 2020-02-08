"use strict";

var gulp = require('gulp'),
    concat = require('gulp-concat'),
    cssnano = require('gulp-cssnano'),
    pump = require('pump'),
    uglify = require('gulp-uglify'),
    gulpif = require('gulp-if'),
    replace = require('gulp-batch-replace'),
    livereload = require('gulp-livereload'),
    strip = require('gulp-strip-comments'),

    production = (process.argv.indexOf('--production') !== -1),
    staging = (process.argv.indexOf('--staging') !== -1),
    jsSrcDir,
    cssSrcDir,
    imgSrcDir,
    fontSrcDir,
    htmlSrcDir,
    pageSrcDir,
    pageSrcDirMob,
    vendorJsDir,
    vendorCssDir,
    baseDir = './',
    output = './gulp_build/',
    replaceList;

replaceList =
    require('../gulp_config/' + (production ? 'production' : staging ? 'staging' : 'local') + '.js');

jsSrcDir = [baseDir + "webApp/app.js", baseDir + "webApp/config.js", baseDir + "webApp/directives.js",
    baseDir + "webApp/main-controller.js", baseDir + "webApp/services/*.js", baseDir + "webApp/core/**/*.js",
    baseDir + "js/angulartics-localytics.js"];
vendorJsDir = [baseDir + "libs/js/jquery/jquery.min.js",
    baseDir + "libs/js/jquery_lazyload/jquery.lazyload.js",
    baseDir + "libs/js/jquery_lazyload/jquery.scrollstop.js",
    baseDir + "libs/js/bootstrap/bootstrap.min.js",
    baseDir + "libs/js/SHA-1/sha1.js",
    baseDir + "libs/js/angular/angular.min.js",
    baseDir + "libs/js/angular-update-meta/update-meta.min.js",
    baseDir + "libs/js/lodash/lodash.min.js",
    baseDir + "libs/js/angular-ui-router/angular-ui-router.min.js",
    baseDir + "libs/js/angular-bootstrap/ui-bootstrap-tpls.min.js",
    baseDir + "libs/js/satellizer/satellizer.min.js",
    baseDir + "libs/js/angular-animate/angular-animate.js",
    baseDir + "libs/js/angular-aria/angular-aria.js",
    baseDir + "libs/js/angular-sanitize/angular-sanitize.min.js",
    baseDir + "libs/js/angular-messages/angular-messages.js",
    baseDir + "libs/js/angulartics/angulartics.min.js",
    baseDir + "libs/js/angulartics-google-analytics/angulartics-ga.min.js",
    baseDir + "libs/js/angular-bootstrap-lightbox/angular-bootstrap-lightbox.min.js"];
cssSrcDir = [baseDir + "css/bumper/bump.css"];
vendorCssDir = [
    baseDir + "libs/css/bootstrap/bootstrap.min.css",
    baseDir + "libs/css/bootstrap/bootstrap-theme.min.css",
    baseDir + "libs/css/angular-bootstrap-lightbox/angular-bootstrap-lightbox.min.css"];
imgSrcDir = [baseDir + "img/**"];
fontSrcDir = [baseDir + "fonts/**"];
htmlSrcDir = [baseDir + "webApp/views/**/*.html"];
pageSrcDir = '../templates/index.html';
pageSrcDirMob ='../templates/m_index.html';

gulp.task('Compile_Styles', function () {
    return gulp.src(cssSrcDir)
        .pipe(cssnano({autoprefixer:false}))
        .pipe(gulp.dest((output) + 'css'));
});
gulp.task('Compress_Vendor_CSS',function () {
    return gulp.src(vendorCssDir)
        .pipe(concat('vendor.min.css'))
        .pipe(cssnano({autoprefixer:false}))
        .pipe(gulp.dest((output) + 'libs/css'));
});
gulp.task('Concat_Bumper_JS', function() {
    return gulp.src(jsSrcDir)
        .pipe(strip())
        .pipe(concat('bumper.min.js', {newLine: ';'}))
        .pipe(gulp.dest((output) + 'js'));
});
gulp.task('Concat_Vendor_JS', function () {
    return gulp.src(vendorJsDir)
        .pipe(strip())
        .pipe(concat('vendor.min.js',{newLine:';'}))
        .pipe(gulp.dest((output) + 'libs/js'));
});
gulp.task('Compile_Vendor_JS', ['Concat_Vendor_JS'], function(cb) {
    var options = {
        mangle: false
    };
    pump([
            gulp.src((output) + 'libs/js/vendor.min.js'),
            uglify(options),
            gulp.dest((output) + 'libs/js')
        ],
        cb
    );
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
gulp.task('Copy_Img', function () {
    return gulp.src(imgSrcDir)
        .pipe(gulp.dest((output) + 'img'));
});
gulp.task('Copy_Fonts', function () {
    return gulp.src(fontSrcDir)
        .pipe(gulp.dest((output) + 'fonts'));
});
gulp.task('Compile_Home_Page', function () {
    return gulp.src(pageSrcDir)
        .pipe(replace(replaceList))
        .pipe(gulp.dest('./public'));
});
gulp.task('Compile_Home_Page_Mobile', function () {
    return gulp.src(pageSrcDirMob)
        .pipe(replace(replaceList))
        .pipe(gulp.dest('./public'));
});
gulp.task('Compile_Views', function () {
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