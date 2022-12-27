function showNextMove() {
    let val = parseInt(sessionStorage.getItem('current_move'));
    let total = parseInt(document.getElementById('total_moves').value);
    if (val < total) {
        val++;
        setCurrentMoveInSession(val);
    }
    showMovesCounter();
    fillResultPuzzleWithCurrentMovePieces();

}
function showPreviousMove() {
    let current_move = parseInt(sessionStorage.getItem('current_move'));
    if (current_move > 0) {
        current_move--;
        setCurrentMoveInSession(current_move);
    }
    showMovesCounter();
    fillResultPuzzleWithCurrentMovePieces();
}
function scrollToResult() {
    var element = document.getElementById("result-sec");
    var top = element.offsetTop;
    var currentTop = window.scrollTop;

    if (top !== currentTop) {
        window.scrollTo(0, top);
    }
}

document.getElementById('form').addEventListener('submit', function (event) {
    sessionStorage.setItem("form_submitted", "1");
    savePuzzle();
});
document.getElementById('reset-btn').addEventListener('click', function (event) {
    sessionStorage.clear();
    hideResultSection();
    hideResetButton();
    showSolveButton();
});

document.getElementById('reset-auto-play-btn').addEventListener('click', function (event) {
    setCurrentMoveInSession("0");
    showMovesCounter();
    fillResultPuzzleWithCurrentMovePieces();
});
document.getElementById('auto-play-btn').addEventListener('click', function (event) {
    let current_move = parseInt(sessionStorage.getItem('current_move'));
    const total_moves = parseInt(document.getElementById('total_moves').value);
    let count = 0;
    count++;
    if (count === total_moves) {
        clearInterval(intervalId);
    }
    // create the interval and store the interval ID
    const intervalId = setInterval(showNextMove, 1000);
});

function fillResultPuzzleWithCurrentMovePieces() {
    let current_move = parseInt(sessionStorage.getItem('current_move'));

    const moves_pieces = document.getElementById('moves').value.split('],');
    const pie = moves_pieces[current_move].replace(/[\[\]]/g, '').split(', ');
    for (let index = 0; index < 9; index++) {
        let value = pie[index].replace(/'/g, '');
        document.getElementById("stepPiece_" + index).value = value === '0' ? '' : value;
    }
}
function showResultSection() {
    if (parseInt(document.getElementById('total_moves').value) >= 1) {
        showArrows();
    } else {
        hideArrows();
    }
    document.getElementById('result-sec').style.display = "block";
    if (!sessionStorage.hasOwnProperty('current_move')) {
        setCurrentMoveInSession("0");
    }
    showMovesCounter();

    fillResultPuzzleWithCurrentMovePieces();

}
function showMovesCounter() {
    document.getElementById('moves_counter').style.display = "block";

    document.getElementById('moves_counter').textContent =
        sessionStorage.getItem('current_move') +
        "/" + document.getElementById('total_moves').value;
}
function setCurrentMoveInSession(value) {
    sessionStorage.setItem('current_move', value);
}
function hideArrows() {
    document.getElementById('left_arrow').style.display = "none";
    document.getElementById('right_arrow').style.display = "none";
}
function showArrows() {
    document.getElementById('left_arrow').style.display = "block";
    document.getElementById('right_arrow').style.display = "block";
}
function hideResultSection() {
    document.getElementById('result-sec').style.display = "none";
}
function hideSolveButton() {
    document.getElementById('start-btn').style.display = "none";
} function showSolveButton() {
    document.getElementById('start-btn').style.display = "block";
}

function showResetButton() {
    document.getElementById('reset-btn').style.display = "block";
}
function hideResetButton() {
    document.getElementById('reset-btn').style.display = "none";
}

window.addEventListener('load', function (request) {
    // sessionStorage.clear();

    if (sessionStorage.getItem("form_submitted") === "1") {
        loadLastPuzzle();
        hideSolveButton();
        showResetButton();
        showResultSection();
        showMovesCounter();
        scrollToResult();
    } else {

        generateRandomPieces('INIT');
        generateRandomPieces('FINAL');
    }

});
function savePuzzle() {
    for (let index = 0; index < 9; index++) {
        sessionStorage.setItem("initStatePiece_" + index,
            document.getElementById("initStatePiece_" + index).value);
    }
    for (let index = 0; index < 9; index++) {
        sessionStorage.setItem("finalStatePiece_" + index,
            document.getElementById("finalStatePiece_" + index).value);
    }
}
function loadLastPuzzle() {
    for (let index = 0; index < 9; index++) {
        document.getElementById("initStatePiece_" + index).value = sessionStorage.getItem("initStatePiece_" + index);
    }
    for (let index = 0; index < 9; index++) {
        document.getElementById("finalStatePiece_" + index).value = sessionStorage.getItem("finalStatePiece_" + index);
    }
}
function generateRandomPieces(state) {
    let values = Array.from({ length: 9 }, (v, k) => k);
    values.sort((a, b) => 0.5 - Math.random());
    if (state == 'INIT') {
        for (let index = 0; index < 9; index++) {
            // document.getElementById("initStatePiece_" + index).value = index == 0 ? '' : index;
            document.getElementById("initStatePiece_" + index).value = values[index] == 0 ? '' : values[index];
        }
    } else if (state = 'FINAL') {
        for (let index = 0; index < 9; index++) {
            // document.getElementById("finalStatePiece_" + index).value = index == 0 ? '' : index;
            document.getElementById("finalStatePiece_" + index).value = values[index] == 0 ? '' : values[index];
        }
    }
}