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

STATIC_URL = (production ? 'https://booking.bumper.com/static/opsPanel/public/' : staging ? 'https://staging.bumper.com/static/opsPanel/public/' : 'http://localhost:8081/static/opsPanel/public/');

gulp.task('Copy_LibFiles', ['Clean_PublicFolder'], function () {
    return gulp.src('libs/**')
        .pipe(gulp.dest('./gulp_build/libs/'));
});

gulp.task('Copy_Chosen_IMG', ['Clean_PublicFolder'], function () {
    return gulp.src('libs/css/chosen/chosen-sprite.png')
        .pipe(gulp.dest('./public/libs/css/chosen/'));
});

// coping plugin files for graphs as it is because getting error otherwise.
gulp.task('Copy_JSVendorPlugins',['Clean_PublicFolder'], function () {
    return gulp.src('js/vendor/plugins/**')
        .pipe(gulp.dest('./public/js/vendor/plugins/'));
});

/* Only to be done in production */
gulp.task('File_Reversion', ['Clean_PublicFolder', 'Concat_Bumper_JS','Compile_Bumper_JS', 'Compile_Styles','Copy_LibFiles',
    'Copy_JSVendorPlugins', 'Copy_Img','Copy_Firebase','Compile_Home_Page', 'Compile_Views','Increase_Version_JS'], function () {
    return gulp.src(['./gulp_build/css/**','./gulp_build/img/**', './gulp_build/img/**',
        './gulp_build/js/**', './gulp_build/libs/**', './gulp_build/views/**','./gulp_build/firebase/**',
            '!./gulp_build/libs/css/fonts/**', '!./gulp_build/libs/css/chosen/chosen-sprite.png'],
        {base: './gulp_build/'})

        .pipe(rev())
        .pipe(revDelOriginal())
        .pipe(gulp.dest('./public/')) // write files to this dir
        .pipe(rev.manifest())
        .pipe(revDel({ dest: 'public', force: true }))
        .pipe(gulp.dest('./')); // write manifest to build dir
});

// This is done due to font files being refered from css files.. where currently we are not replacing.
gulp.task('Copy_FontFiles',['Clean_PublicFolder'], function () {
    return gulp.src('libs/css/fonts/**')
        .pipe(gulp.dest('./public/libs/css/fonts/'));
});

gulp.task("Replace_Rev_In_Files", ["File_Reversion"], function(){
    var manifest = gulp.src("./rev-manifest.json");
    return gulp.src(["./public/index.html", "./public/views/**/*.html", "./public/js/**", "./public/firebase/**"], {base: './public/'})
        .pipe(revReplace({manifest: manifest, prefix: STATIC_URL})) // can use , prefix:'/dist' option here /css/abc.css /dist/css/abc.css
        .pipe(gulp.dest("./public/"));
        //.pipe(livereload());
});

taskList.push('Clean_PublicFolder');
taskList.push('Concat_vendor_JS');
taskList.push('Compile_vendor_JS');
taskList.push('Concat_Bumper_JS');
taskList.push('Compile_Bumper_JS');
taskList.push('Compile_Styles');
taskList.push('Copy_Img');
taskList.push('Copy_Firebase');
taskList.push('Compile_Home_Page');
taskList.push('Compile_Views');
taskList.push('Increase_Version_JS');
taskList.push('Copy_LibFiles');
taskList.push('Copy_Chosen_IMG');
taskList.push('Copy_JSVendorPlugins');
taskList.push('File_Reversion');
taskList.push('Copy_FontFiles');
taskList.push('Replace_Rev_In_Files');

gulp.task('default', taskList, function () {
    console.log("Watching files...");
    //livereload.listen();
    gulp.watch(['./opsApp/**', '../../templates/ops-panel/index.html'], taskList);
     // Create LiveReload server
});
