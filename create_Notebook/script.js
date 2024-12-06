// script.js
document.getElementById('saveButton').addEventListener('click', function() {
    // メモを取得
    const memoInput = document.getElementById('memoInput');
    const memoText = memoInput.value;

    // メモが空でない場合に保存
    if (memoText.trim() !== '') {
        // ローカルストレージから既存のメモを取得
        let savedMemos = JSON.parse(localStorage.getItem('memos')) || [];

        // 新しいメモを配列に追加
        savedMemos.push(memoText);

        // ローカルストレージにメモを保存
        localStorage.setItem('memos', JSON.stringify(savedMemos));

        // メモを表示
        displayMemos();
        
        // 入力欄をクリア
        memoInput.value = '';
    }
});

// メモを表示する関数
function displayMemos() {
    const memoList = document.getElementById('memoList');
    memoList.innerHTML = '';  // 既存のリストをクリア

    // ローカルストレージからメモを取得
    const savedMemos = JSON.parse(localStorage.getItem('memos')) || [];

    // メモがある場合、リストに追加
    savedMemos.forEach(function(memo) {
        const li = document.createElement('li');
        li.textContent = memo;
        memoList.appendChild(li);
    });
}

// ページ読み込み時にメモを表示
window.onload = function() {
    displayMemos();
};
