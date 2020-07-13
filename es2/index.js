
let textPath = "text_data_modified/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt";
// let textPath = "text_data_modified/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt";
// let textPath = "text_data_modified/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt";

const fs = require('fs');
const stopwords = getStopwords("resources/stopwords.txt");
const nasari = parseNasari("resources/dd-small-nasari-15.txt");
const compressionRate = 20;
const precision = 10;
let textToSummarize = getLines(textPath);

summarizeText();

function parseNasari(path) {
    let rules = getLines(path);
    var nasari = [];

    rules.forEach(p => {
        let parts = p.split(';');

        let terms = parts.slice(2);
        let synsets = [];
        for(var t = 0; t < terms.length; t++){
            let synset = getTermWeigth(terms[t]);
            synsets.push(synset);
        }
        let word = {
            bbID: parts[0],
            title: parts[1],
            synset: synsets
        };
        nasari.push(word);
    });

    return nasari;
}

function numCompressedWord (){
    return getTextLength() - Math.floor((getTextLength()*compressionRate)/100);
}

function getStopwords(path) {
    return fs.readFileSync(path, 'utf-8').split('\n');
}

function getLines(path){
    return fs.readFileSync(path, 'utf-8')
           .split('\n')
           .filter(l =>{return !l.startsWith('#') && l !== ''});
}

function getTextLength() {
    let numWord = 0;
    textToSummarize.forEach(l =>{
        let line = l.split(" ");
        numWord += line.length;
    });
    return numWord;
}

function getTermWeigth(term) {
    let ww = term.split("_");
    return {word: ww[0], score: ww[1]}
}

function extractVectors(word) {
    let res = [];
    let set = getConceptSet(word);
    set.forEach(s =>{
       res.push(s.synset);
    });

    return res;
}

function getConceptSet(word) {
    let capitalLetterWord = word.charAt(0).toUpperCase() + word.slice(1);
    let filterRes = nasari.filter(v => {return capitalLetterWord === v.title});

    return filterRes;
}

// context: select the most common words in the text given a precision
function createContext(precision){
    let words = [];
    let score = [];
    let occurrenceArray =[];
    let title = textToSummarize.join(" ").split(" ");

    title.forEach(w => {
        let lowerW = w.toLowerCase();
        if(!stopwords.includes(lowerW)){
            if(!words.includes(lowerW)){
                words.push(lowerW);
                score.push(1);
            }
            else {
                let i = words.indexOf(lowerW);
                score[i]++;
            }
        }

    });
    for(let i = 0; i< score.length;i++){
        occurrenceArray.push({lemma: words[i], num : score[i]})

    }
    occurrenceArray.sort((a,b)=>{
        let cmp = -1;
        if(a.num < b.num)
            cmp = 1;

        return cmp;
    });

    let tmp = occurrenceArray.slice(0,precision);
    let context =[];
    tmp.forEach(i =>{
        context.push(i.lemma);
    });

    return context;
}

function computeSimilarity(w1, w2){
    let results = [];
    let cw1 = extractVectors(w1);
    let cw2 = extractVectors(w2);

    // if no vector is found similarity is 0.1 for smoothing prob
    if(cw1.length < 1 || cw2.length < 1){return 0.1;}

    cw1.forEach( v1 =>{
        cw2.forEach(v2 =>{
            // foreach couple of senses of w1 and w2
            let wo = Math.sqrt(weightedOverlap(v1,v2));
            results.push(wo);
        });
    });

    return Math.max.apply(Math, results);
}

function weightedOverlap(v1, v2) {
    let result = 0;
    let num = 0;
    let overDim = [];
    for(let i = 0; i < v1.length; i++ ){
        for(let j = 0; j < v2.length; j++ ){
            if(v1[i].word === v2[j].word){
                // numerator: rank(q,v1) + rank(q,v2) ^-1
                num += Math.pow(i+j+2, -1);
                overDim.push(v1[i].word);
            }
        }
    }
    let den = 0;
    for(let i = 1; i <= overDim.length; i++){
        // denominator: sum(2*i) ^-1
        den += Math.pow(2*i, -1);
    }
    if(den > 0)
        result = num/den;

    return result;
}

function summarizeText(){
    let n = numCompressedWord();
    let m = getTextLength();
    let i = 1;

    while(m > n){
        let context = createContext(precision);
        let score = getParagraphScore(context);

    //    rerank using title
        let rerankContext = textToSummarize[0].split(" ");
        let score2 = getParagraphScore(rerankContext);
        let sum = score.map((num, idx) =>{return num + score2[idx];});

        let minElem = Math.min.apply(Math, sum);
        let minIndex = sum.indexOf(minElem);

        textToSummarize.splice(minIndex,1);
        i++;
        m = getTextLength();
    }
    console.log(textToSummarize);
    return textToSummarize;

}

function getParagraphScore(context) {
    let score = [];

    textToSummarize.forEach(l => {
        let words = l.split(" ");
        let lineScore = 0;
        context.forEach(c =>{
            words.forEach(w =>{
                lineScore += computeSimilarity(c,w);
            });
        });
        score.push(lineScore);
    });
    return score;
}