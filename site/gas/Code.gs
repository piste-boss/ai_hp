// ============================================
// Google Apps Script - お問い合わせフォーム処理
// 1. スプレッドシートに転記
// 2. Resend API で管理者通知メール送信
// 3. Resend API でお客様に自動返信メール送信
// ============================================

// === 設定 ===
// スクリプトプロパティから取得（GASエディタ → プロジェクトの設定 → スクリプトプロパティで設定）
const RESEND_API_KEY = PropertiesService.getScriptProperties().getProperty('RESEND_API_KEY');
const ADMIN_EMAIL = 'info@piste-i.com';
const FROM_EMAIL = 'info@piste-i.com';
const FROM_NAME = 'Piste AI EVANGELISTS';

// === POST受信（お問い合わせ & Stripe Webhook 兼用） ===
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    // Stripe Webhookの場合
    if (data.type && data.type === 'checkout.session.completed') {
      handleStripeCheckout(data);
      return ContentService
        .createTextOutput(JSON.stringify({ status: 'ok' }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // お問い合わせフォームの場合
    writeToSheet(data);
    sendAdminNotification(data);
    sendAutoReply(data);

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    Logger.log('Error: ' + error.message);
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// === Stripe決済完了処理 ===
function handleStripeCheckout(event) {
  const session = event.data.object;
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName('決済情報');

  if (!sheet) {
    sheet = ss.insertSheet('決済情報');
    sheet.appendRow([
      'タイムスタンプ', '氏名', 'メールアドレス',
      'プラン', '金額', '通貨', 'ステータス',
      'Stripe顧客ID', 'セッションID', 'サブスクリプションID'
    ]);
    sheet.getRange(1, 1, 1, 10).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }

  // 顧客情報を取得
  const name = session.customer_details ? session.customer_details.name || '' : '';
  const email = session.customer_details ? session.customer_details.email || '' : '';

  // プラン名（金額で判定）
  const amount = session.amount_total || 0;
  const planMap = {
    2500: 'Claude Code 基礎＆セットアップ動画',
    3000: 'Claude Code 導入サポート（スポット）',
    18000: 'ライトプラン（月額）',
    32000: 'スタンダードプラン（月額）',
    90000: 'プラチナプラン（月額）'
  };
  const plan = planMap[amount] || '不明（' + amount + '円）';

  sheet.appendRow([
    new Date(),
    name,
    email,
    plan,
    amount,
    session.currency || 'jpy',
    session.payment_status || '',
    session.customer || '',
    session.id || '',
    session.subscription || ''
  ]);

  Logger.log('✅ 決済情報記録: ' + name + ' / ' + plan);

  // 管理者に決済通知メール
  sendPaymentNotification(name, email, plan, amount);

  // 動画商品の場合、購入者に動画リンクを送信
  const VIDEO_PRODUCTS = {
    2500: {
      name: 'Claude Code 基礎＆セットアップ動画',
      driveUrl: 'https://drive.google.com/file/d/1xrRfpfC8gGvj6pQWij48aNr12u2DZW2_/view?usp=drivesdk'
    }
  };

  if (VIDEO_PRODUCTS[amount] && email) {
    sendVideoDelivery(name, email, VIDEO_PRODUCTS[amount]);
  }
}

// === 決済通知メール ===
function sendPaymentNotification(name, email, plan, amount) {
  const subject = '【決済完了】' + name + ' 様 - ' + plan;

  const html = `
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #333; border-bottom: 2px solid #27ae60; padding-bottom: 10px;">決済完了通知</h2>
      <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px; font-weight: bold; width: 120px; color: #666;">プラン</td>
          <td style="padding: 10px;">${plan}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px; font-weight: bold; color: #666;">金額</td>
          <td style="padding: 10px;">&yen;${amount.toLocaleString()}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px; font-weight: bold; color: #666;">氏名</td>
          <td style="padding: 10px;">${name}</td>
        </tr>
        <tr>
          <td style="padding: 10px; font-weight: bold; color: #666;">メール</td>
          <td style="padding: 10px;">${email}</td>
        </tr>
      </table>
    </div>
  `;

  sendViaResend(ADMIN_EMAIL, subject, html);
}

// === 動画配信メール ===
function sendVideoDelivery(name, email, video) {
  const subject = '【Piste AI EVANGELISTS】動画のお届け - ' + video.name;

  const html = `
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
      <div style="background: #1a1a1a; padding: 20px; text-align: center;">
        <h1 style="color: #c4a24e; font-size: 1.2em; margin: 0;">Piste AI EVANGELISTS</h1>
      </div>

      <div style="padding: 30px 20px;">
        <p>${name || ''} 様</p>
        <p>この度はご購入いただき、誠にありがとうございます。<br>
        以下のリンクから動画をご視聴いただけます。</p>

        <div style="background: #f8f7f4; padding: 25px; border-radius: 8px; margin: 25px 0; text-align: center;">
          <p style="font-weight: bold; font-size: 1.1em; margin-bottom: 15px;">${video.name}</p>
          <a href="${video.driveUrl}" style="display: inline-block; background: #c4a24e; color: #fff; text-decoration: none; padding: 12px 40px; border-radius: 6px; font-weight: bold;">動画を視聴する</a>
        </div>

        <p style="font-size: 0.85em; color: #888;">
          ※ このリンクはご購入者様専用です。第三者への共有はご遠慮ください。<br>
          ※ ご不明点がございましたら、お気軽にお問い合わせください。
        </p>

        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

        <p style="font-size: 0.85em; color: #888;">
          Piste AI EVANGELISTS<br>
          メール: info@piste-i.com<br>
          LINE: <a href="https://lin.ee/Pul5f6V">https://lin.ee/Pul5f6V</a>
        </p>
      </div>
    </div>
  `;

  sendViaResend(email, subject, html);
  Logger.log('✅ 動画配信メール送信: ' + email + ' / ' + video.name);
}

// === カテゴリ値を日本語ラベルに変換 ===
const CATEGORY_MAP = {
  'claude-code': 'Claude Code 導入サポート（スポット）',
  'light': 'ライトプラン（月額）',
  'standard': 'スタンダードプラン（月額）',
  'platinum': 'プラチナプラン（月額）',
  'general': 'AI導入について相談したい',
  'other': 'その他'
};

function getCategoryLabel(value) {
  return CATEGORY_MAP[value] || value || '未選択';
}

// === スプレッドシート転記 ===
const SPREADSHEET_ID = '1ZUU53yUvWp-NYf5MCr70cS5cKilcJO1dl7dPvXIqu8A';

function writeToSheet(data) {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName('問い合わせ');

  // シートがなければ作成
  if (!sheet) {
    sheet = ss.insertSheet('問い合わせ');
    sheet.appendRow(['タイムスタンプ', 'お名前', '会社名', 'メールアドレス', 'ご相談内容', 'メッセージ']);
  }

  sheet.appendRow([
    new Date(),
    data.name || '',
    data.company || '',
    data.email || '',
    getCategoryLabel(data.category),
    data.message || ''
  ]);
}

// === Resend API メール送信 ===
function sendViaResend(to, subject, html) {
  const payload = {
    from: FROM_NAME + ' <' + FROM_EMAIL + '>',
    to: [to],
    subject: subject,
    html: html
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'Bearer ' + RESEND_API_KEY
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch('https://api.resend.com/emails', options);
  Logger.log('Resend response: ' + response.getContentText());
  return response;
}

// === 管理者通知メール ===
function sendAdminNotification(data) {
  const subject = '【お問い合わせ】' + (data.name || '名前未入力') + ' 様より';

  const html = `
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #333; border-bottom: 2px solid #c4a24e; padding-bottom: 10px;">新しいお問い合わせ</h2>
      <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px; font-weight: bold; width: 120px; color: #666;">お名前</td>
          <td style="padding: 10px;">${data.name || ''}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px; font-weight: bold; color: #666;">会社名</td>
          <td style="padding: 10px;">${data.company || '未入力'}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px; font-weight: bold; color: #666;">メールアドレス</td>
          <td style="padding: 10px;">${data.email || ''}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px; font-weight: bold; color: #666;">ご相談内容</td>
          <td style="padding: 10px;">${getCategoryLabel(data.category)}</td>
        </tr>
        <tr>
          <td style="padding: 10px; font-weight: bold; color: #666;">メッセージ</td>
          <td style="padding: 10px; white-space: pre-wrap;">${data.message || ''}</td>
        </tr>
      </table>
    </div>
  `;

  sendViaResend(ADMIN_EMAIL, subject, html);
}

// === お客様への自動返信メール ===
function sendAutoReply(data) {
  if (!data.email) return;

  const subject = '【Piste AI EVANGELISTS】お問い合わせありがとうございます';

  const html = `
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
      <div style="background: #1a1a1a; padding: 20px; text-align: center;">
        <h1 style="color: #c4a24e; font-size: 1.2em; margin: 0;">Piste AI EVANGELISTS</h1>
      </div>

      <div style="padding: 30px 20px;">
        <p>${data.name || ''} 様</p>
        <p>この度はお問い合わせいただき、誠にありがとうございます。<br>
        以下の内容で承りました。</p>

        <div style="background: #f8f7f4; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <p style="margin: 5px 0;"><strong>お名前：</strong>${data.name || ''}</p>
          <p style="margin: 5px 0;"><strong>会社名：</strong>${data.company || '未入力'}</p>
          <p style="margin: 5px 0;"><strong>ご相談内容：</strong>${getCategoryLabel(data.category)}</p>
          <p style="margin: 5px 0;"><strong>メッセージ：</strong></p>
          <p style="margin: 5px 0; white-space: pre-wrap;">${data.message || ''}</p>
        </div>

        <p>内容を確認の上、2営業日以内にご連絡いたします。<br>
        しばらくお待ちくださいませ。</p>

        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

        <p style="font-size: 0.85em; color: #888;">
          Piste AI EVANGELISTS<br>
          メール: info@piste-i.com<br>
          LINE: <a href="https://lin.ee/Pul5f6V">https://lin.ee/Pul5f6V</a>
        </p>
      </div>
    </div>
  `;

  sendViaResend(data.email, subject, html);
}

// === テスト関数（GASエディタから手動実行） ===
function testAll() {
  const testData = {
    name: 'テスト太郎',
    company: 'テスト株式会社',
    email: 'pistei.com2019@gmail.com',
    category: 'standard',
    message: 'テスト送信です'
  };

  Logger.log('=== テスト開始 ===');

  // スプレッドシート書き込みテスト
  try {
    writeToSheet(testData);
    Logger.log('✅ スプレッドシート書き込み成功');
  } catch (err) {
    Logger.log('❌ スプレッドシートエラー: ' + err.message);
  }

  // 管理者メールテスト
  try {
    sendAdminNotification(testData);
    Logger.log('✅ 管理者メール送信成功');
  } catch (err) {
    Logger.log('❌ 管理者メールエラー: ' + err.message);
  }

  // 自動返信メールテスト
  try {
    sendAutoReply(testData);
    Logger.log('✅ 自動返信メール送信成功');
  } catch (err) {
    Logger.log('❌ 自動返信メールエラー: ' + err.message);
  }

  Logger.log('=== テスト完了 ===');
}

// === CORS対応（プリフライトリクエスト） ===
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);
}
