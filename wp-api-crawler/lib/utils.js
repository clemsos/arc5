function slugify(text) {
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
    .replace(/^-+/, '')             // Trim - from start of text
    .replace(/-+$/, '');            // Trim - from end of text
}

function levenshtein(str1, str2) {
    var cost = new Array(),
        n = str1.length,
        m = str2.length,
        i, j;

    var minimum = function(a, b, c) {
        var min = a;
        if (b < min) {
            min = b;
        }
        if (c < min) {
            min = c;
        }
        return min;
    }

    if (n == 0) {
        return;
    }
    if (m == 0) {
        return;
    }

    for (var i = 0; i <= n; i++) {
        cost[i] = new Array();
    }

    for (i = 0; i <= n; i++) {
        cost[i][0] = i;
    }

    for (j = 0; j <= m; j++) {
        cost[0][j] = j;
    }

    for (i = 1; i <= n; i++) {
        var x = str1.charAt(i - 1);

        for (j = 1; j <= m; j++) {
            var y = str2.charAt(j - 1);

            if (x == y) {
                cost[i][j] = cost[i - 1][j - 1];
            } else {
                cost[i][j] = 1 + minimum(cost[i - 1][j - 1], cost[i][j - 1], cost[i - 1][j]);
            }

        } //endfor

    } //endfor

    return cost[n][m];
}

function isSimilar (str1, str2) {
    return (levenshtein(str1, str2) < 10) ? true : false;
}

// from 2 arrays return a pair array
function matchSimilarItemsInArray(arr1, arr2){
    var similars = [];
    for (var i = 0; i < arr1.length; i++) {
        for (var j = 0; j < arr2.length; j++) {
            if( isSimilar(arr1[i], arr2[j]) ) similars.push([i,j])
        }
    }
    return similars;
}

module.exports = {
    isSimilar : isSimilar,
    matchSimilarItemsInArray : matchSimilarItemsInArray,
    slugify : slugify
}
