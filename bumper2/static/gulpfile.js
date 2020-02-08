"use strict";

require('./gulp_tasks/modules.tasks.js');

var gulp = require('gulp'),
    livereload = require('gulp-livereload'),
    rev = require('gulp-rev'),
    revDelOriginal = require('gulp-rev-delete-original'),
    revReplace = require('gulp-rev-replace'),
    revDel = require('rev-del'),
    production = (process.argv.indexOf('--production') !== -1),
    staging = (process.argv.indexOf('--staging') !== -1),
    STATIC_URL,
    taskList = [];

STATIC_URL = (production ? 'https://d18qyvmj2t58jj.cloudfront.net/' : staging ? 'https://staging.bumper.com/static/public/' : 'http://localhost:8081/static/public/');


 gulp.task('Copy_fontsLibFiles', function () {
     return gulp.src('libs/fonts/**')
         .pipe(gulp.dest('./gulp_build/libs/fonts/'));
 });

/* Only to be done in production */
gulp.task('File_Reversion', ['Concat_Bumper_JS','Compile_Bumper_JS','Concat_Vendor_JS','Compile_Vendor_JS','Compile_Styles','Compress_Vendor_CSS','Copy_fontsLibFiles', 'Copy_Img',
    'Copy_Fonts','Compile_Home_Page','Compile_Home_Page_Mobile', 'Compile_Views','Increase_Version_JS'], function () {
    return gulp.src(['./gulp_build/css/**','./gulp_build/fonts/**','./gulp_build/img/**',
        './gulp_build/js/**', './gulp_build/libs/**', './gulp_build/views/**'], {base: './gulp_build/'})
        .pipe(rev({dontRenameFile: [/^\/favicon.ico$/g, '.html'] }))
        .pipe(revDelOriginal())
        .pipe(gulp.dest('./public/')) // write files to this dir
        .pipe(rev.manifest())
        .pipe(revDel({ dest: 'public', force: true }))
        .pipe(gulp.dest('./')); // write manifest to build dir
});

gulp.task("Replace_Rev_In_Files", ["File_Reversion"], function(){
    var manifest = gulp.src("./rev-manifest.json");
    return gulp.src(["./public/index.html","./public/m_index.html" ,"./public/views/**", "./public/js/**", "./public/css/**"], {base: './public/'})
        .pipe(revReplace({manifest: manifest, prefix: STATIC_URL})) // can use , prefix:'/dist' option here /css/abc.css /dist/css/abc.css
        .pipe(gulp.dest("./public/"));
        //.pipe(livereload());
});

taskList.push('Concat_Bumper_JS');
taskList.push('Compile_Bumper_JS');
taskList.push('Concat_Vendor_JS');
taskList.push('Compile_Vendor_JS');
taskList.push('Compile_Styles');
taskList.push('Copy_Img');
taskList.push('Copy_Fonts');
taskList.push('Compile_Home_Page');
taskList.push('Compile_Home_Page_Mobile');
taskList.push('Compile_Views');
taskList.push('Increase_Version_JS');
taskList.push('Copy_fontsLibFiles');
taskList.push('File_Reversion');
taskList.push('Replace_Rev_In_Files');

gulp.task('default', taskList, function () {
    console.log("Watching files...");

    //livereload.listen();
    gulp.watch(['./webApp/**', './css/**', './img/**', '../templates/index.html','../templates/m_index.html',
        "./fonts/**", "./js/**", "./libs/**"], taskList);
     // Create LiveReload server
});
