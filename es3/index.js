const fs = require('fs');
const similarity = require( 'compute-cosine-similarity' );
var request = require('sync-request');

const couples = parseDataFile("resources/it.test.data.tsv");
const nasari = parseNasari("resources/mini_NASARI.tsv");
const bbnet = getSensesDictionary("resources/SemEval17_IT_senses2synsets.txt");

couples.forEach( c =>{
    let result = senseIdentification(c.w1, c.w2);
    if (result.length > 0) {
        let s1 = result[0].sense1;
        let s2 = result[0].sense2;
        let score = result[0].score;
        let nasariSim = mapRange([-1,1], [0,4], score);

        console.log("### Word1: " + c.w1 + " - Word2: " + c.w2 + " ###");
        console.log(" -> Best Sense Word1: " + s1+ " -> Gloss: " + getGlossFromBabelnet(s1));
        console.log(" -> Best Sense Word2: " + s2+ " -> Gloss: " + getGlossFromBabelnet(s2));
        console.log(" -> Best Nasari Similarity " + nasariSim);
        console.log(" -> Annotated Similarity " + c.score +"\n");

    }

});




function getLines(path){
    return fs.readFileSync(path, 'utf-8')
        .split('\n')
        .filter(l =>{return l !== ''});
}

function parseDataFile(path) {
    let lines = getLines(path);
    let words = [];

    lines.forEach(l => {
        let data = l.split("\t");
        words.push({w1:data[0].toLowerCase(), w2: data[1].toLowerCase(), score: data[2]})

    });
    return words;
}

function parseNasari(path) {
    let nasari = [];
    let lines = getLines(path);

    lines.forEach(l => {
        let bbnetID = l.split("__")[0];
        let vector = l.split("__")[1];
        let embedded = vector.split("\t");
        let wikiTitle = embedded[0].replace(/_/g, ' ').toLowerCase();
        embedded.splice(0, 1);
        nasari[bbnetID] = {vector: embedded, title: wikiTitle};
    });

    return nasari;
}

function getSensesDictionary(path) {
    let ids = [];
    let lines = getLines(path);
    let lemma;

    lines.forEach(l =>{
        if(l.startsWith("#")){
            lemma = l.split("#")[1];
            ids.push({lemma: lemma.toLowerCase(), bbnet: []});
            return;
        }
        ids[ids.length-1].bbnet.push(l);
    });

    return ids;
}

function getSenses(lemma){
    let i =  bbnet.filter( o => {return o.lemma === lemma});
    if(i.length > 0)
        return i[0].bbnet;
    else return [];
}

/* 
* Input: word1 and word2
* Output: list of all possible senses couple and their 
* similarity score ordered by score
*/
function senseIdentification(w1, w2) {
    let senses = [];
    let senses1 = getSenses(w1);
    let senses2 = getSenses(w2);

    senses1.forEach(s1 => {
        let v1;
        if(nasari[s1]){
            v1 = nasari[s1].vector;
        }
        senses2.forEach(s2 => {
            let v2;
            if(nasari[s2]){
                v2 = nasari[s2].vector;
            }
            if(v1 && v2) {
                // compute cosine similarity
                let score = similarity(v1, v2);
                senses.push({score: score, sense1: s1, sense2: s2})
            }
        });
    });

    senses.sort((a,b)=>{
        let cmp = -1;
        if(a.score < b.score)
            cmp = 1;
        return cmp;
    });

    return senses;
}

function mapRange(from, to, s) {
    return (to[0] + (s - from[0]) * (to[1] - to[0]) / (from[1] - from[0])).toFixed(1);
}

function getGlossFromBabelnet(sysnet){
    let url = 'https://babelnet.io/v5/getSynset?id='+sysnet+'&key=27ca9b69-a220-4173-be9d-ce8ff3826080';
    let res = request('GET', url);
    return JSON.parse(res.getBody('utf8'))['glosses'][0].gloss;
}
