---
title: Xây dựng hệ thống RAG cho AI agent
date: "2025-03-30T06:30:00+07:00"
tags:
- ai
- rag
- redisearch
categories:
- AI
description: |
    Ngày nay, AI đã trở thành một công cụ không thể thiếu trong công việc hằng ngày, đặc biệt là đối với dân văn phòng và lập trình viên. Tuy nhiên, các mô hình AI hiện tại vẫn gặp nhiều hạn chế trong việc truy cập và xử lý thông tin.

    Vì vậy, trong bài viết này, mình sẽ giới thiệu một phương pháp giúp nâng cao khả năng tìm kiếm thông tin của AI cũng như cải thiện cách AI truy xuất dữ liệu một cách hiệu quả hơn.
---


## AI và con người: Sự tương đồng trong tìm kiếm và xử lý thông tin

AI và con người đều có những đặc điểm chung, đặc biệt trong việc tìm kiếm và xử lý thông tin. Vì vậy, cả chúng ta và AI đều phải đối mặt với những thách thức tương tự trong quá trình này. Để hiểu rõ hơn, hãy bắt đầu từ chính con người – cách chúng ta tìm kiếm và xử lý thông tin.

Giả sử bạn là một người thông minh, có khả năng phân tích và xử lý thông tin tốt. Tuy nhiên, bạn không thể biết mọi thứ. Khi gặp một khái niệm mới, chẳng hạn như “RAG”, bộ não của bạn sẽ vận hành theo quy trình sau:

1.	Kiểm tra kiến thức hiện có: Bạn đã biết về RAG chưa? Nếu chưa, bước tiếp theo là tìm kiếm thông tin.
2.	Tìm kiếm thông tin: Bạn lên Google và nhập từ khóa “RAG”.
3.	Lọc và đọc thông tin: Bạn xem xét các kết quả trả về, chọn ra những nguồn phù hợp nhất và đọc chúng.
4.	Phân tích và tổng hợp: Bạn xử lý thông tin vừa thu thập để hiểu rõ hơn về RAG.
5.	Đưa ra câu trả lời: Dựa trên thông tin đã phân tích, bạn trả lời câu hỏi.

Quy trình này cũng áp dụng cho AI. Mặc dù AI không thể “biết” mọi thứ, nhưng nó có khả năng tìm kiếm, phân tích và tổng hợp thông tin một cách hiệu quả dựa trên dữ liệu đầu vào.

## Hiểu đơn giản về RAG

RAG (Retrieval-Augmented Generation) là một phương pháp giúp AI tìm kiếm và sử dụng thông tin một cách hiệu quả hơn.

Một hệ thống RAG điển hình bao gồm hai thành phần chính:

-	Bộ tìm kiếm thông tin: Tìm kiếm trong kho dữ liệu lớn và trả về những kết quả liên quan nhất đến truy vấn.
-	Bộ xử lý thông tin: Phân tích dữ liệu tìm được cùng với truy vấn để đưa ra câu trả lời chính xác.

Nhờ RAG, AI có thể khai thác thông tin từ nguồn dữ liệu bên ngoài thay vì chỉ dựa vào kiến thức có sẵn, giúp nâng cao độ chính xác và tính cập nhật của câu trả lời.


## Chuẩn bị

Trong bài viết này, mình sẽ sử dụng RediSearch làm bộ tìm kiếm thông tin và mô hình Llama 3.1 thông qua Ollama.

Dưới đây là thông tin và hướng dẫn cài đặt:

- RediSearch [https://redis.io/docs/latest/develop/interact/search-and-query/](https://redis.io/docs/latest/develop/interact/search-and-query/)
- Ollama [https://ollama.com](https://ollama.com)

## Xây dựng bộ tìm kiếm thông tin

### 1. Ingest dữ liệu

Trong bài viết này, bộ dữ liệu đầu vào là toàn bộ email của mình, được đẩy vào RediSearch để phục vụ tìm kiếm.

Mỗi email sau khi tải về từ Gmail sẽ được vector hóa bằng thuật toán embedding. Mình sẽ đi sâu hơn vào quá trình này trong các bài viết sau.

Hiện tại, bạn chỉ cần hiểu rằng dữ liệu đầu vào ban đầu có độ dài biến đổi (variable length), nhưng cần được chuyển đổi thành dạng có độ dài cố định (fixed length). Cụ thể, mình sử dụng vector có 384 chiều để biểu diễn mỗi email.

Sau khi dữ liệu được vector hóa, thuật toán KNN (K-Nearest Neighbors) sẽ được sử dụng để tìm kiếm những email có nội dung liên quan nhất, giúp AI mô hình truy xuất thông tin hiệu quả.

Công cụ và thư viện sử dụng

Mình sử dụng Python cùng với các thư viện sau:

```
google-api-python-client==2.122.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.0
redis>=5.2.1
sentence-transformers>=4.0.1
```

Đoạn code dưới để lấy crendentials từ google. File credentials.json là một service account key các bạn có thể tạo trên Console của Google Cloud Platform.

```python
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def get_gmail_service():
    """Gets Gmail API service instance."""
    creds = None
    pickle_file = os.path.join(ROOT_DIR, 'etc', 'token.pickle')

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(ROOT_DIR, 'etc', 'credentials.json'), SCOPES)

            # Default port that matches Google Cloud Console's default redirect URI
            creds = flow.run_local_server(port=8000)

        # Save the credentials for the next run
        with open(pickle_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)
```

Function này sẽ lấy danh sách email từ start_date đến end_date bằng Gmail query

```python
def get_list_emails(service, start_date=None, end_date=None):
    # Construct date query if dates provided
    query = ""
    if start_date:
        query += f"after:{start_date} "
    if end_date:
        query += f"before:{end_date}"
        
    # Get all message IDs first
    print("Fetching email IDs...")
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    # Keep getting messages if there are more pages
    while 'nextPageToken' in results:
        results = service.users().messages().list(
            userId='me',
            q=query,
            pageToken=results['nextPageToken']
        ).execute()
        messages.extend(results.get('messages', []))
        
    total_emails = len(messages)
    print(f"Found {total_emails} emails")

    return messages
```


```python
def get_detail_email(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    body = ""
    try:
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':  # Can also check for 'text/html'
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        else:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
    except Exception:
        body = ""

    # Extract headers
    headers = message['payload']['headers']
    email_data = {
        'id': msg_id,
        'subject': '',
        'from': '',
        'date': '',
        'snippet': message['snippet'],
        'body': body,
    }

    # Get relevant headers
    for header in headers:
        name = header['name'].lower()
        if name == 'subject':
            email_data['subject'] = header['value']
        elif name == 'from':
            email_data['from'] = header['value']
        elif name == 'date':
            email_data['date'] = header['value']
            
    return email_data
```

Từ những function trên, chúng ta có thể lấy emails như sau. Generator sẽ lấy tuần tự từng email

```python
g_service = get_gmail_service()
list_emails = get_list_emails(g_service, '2024/01/01', '2024/12/31')
emails_generator = (get_detail_email(g_service, email['id']) for email in list_emails)
```

```python
def get_redis(db=0):
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=db, decode_responses=True)
```

Chúng ta sử dụng mô hình __all-MiniLM-L6-v2__, một mô hình đơn giản nhưng có hiệu năng cao. Vì nội dung email thường không quá dài hay phức tạp, nên mô hình này là lựa chọn phù hợp. Nó sẽ chuyển đổi văn bản thành embedding vector có 384 chiều.

Ngoài ra, bạn cũng có thể sử dụng AI model từ Ollama để thực hiện vector hóa mà không cần import thêm thư viện bên ngoài.

```python
def embed_text(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(text).astype(np.float32).tobytes()
```

Chúng ta lưu trữ email trong Redis dưới dạng hashmap, bao gồm các thông tin lấy từ Gmail và một trường bổ sung chứa embedding của email.

```python
def store_in_redis(redis_client, email, embedding_vector):
    email_data = {
        "id": email['id'],
        "subject": email['subject'],
        "sender": email['from'],
        "date": email['date'],
        "snippet": email['snippet'],
        "body": email['body']
    }
    
    redis_client.hset(f"{REDIS_EMAIL_PREFIX_KEY}{email['id']}", mapping={
        **email,
        "embedding": embedding_vector
    }) 
```


Bây giờ, chúng ta sẽ thiết lập pipeline để ingest dữ liệu.
__embedding_vector__ chính là vector biểu diễn mà mình đã đề cập trước đó. Nó được tạo từ các thông tin quan trọng của email, bao gồm __sender__ (người gửi), __subject__ (tiêu đề) và __snippet__ (đoạn trích nội dung).

```python
g_service = get_gmail_service()
redis_client = get_redis()

list_emails = get_list_emails(g_service, '2024/01/01', '2024/12/31')
emails_generator = (get_detail_email(g_service, email['id']) for email in list_emails)

for email in emails_generate:
    embed_text = f'sender:{email_data["sender"]} subject:{email_data["subject"]} snippet:{email_data["snippet"]}'
    embedding_vector = embed_text(embed_text)

    store_in_redis(redis_client, email, embedding_vector)
```

Sau khi ingest dữ liệu thành công, bước tiếp theo là đánh index để tối ưu hiệu suất tìm kiếm trong Redis.

Trong cấu hình, mình thiết lập trường embedding dưới dạng vector 384 chiều và sử dụng khoảng cách cosine để so sánh độ tương đồng giữa các vector. Bạn có thể tìm hiểu thêm về cosine similarity tại đây:

[https://en.wikipedia.org/wiki/Cosine_similarity](https://en.wikipedia.org/wiki/Cosine_similarity)


```python
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

def create_index_emails():
    r = utils.get_redis(0)
    vector_dim = 384

    # drop old index
    try:
        r.ft('email_idx').dropindex(delete_documents=False)
    except Exception:
        pass

    schema = (
        TextField("id"),
        TextField("subject"),
        TextField("sender"), 
        TextField("date"),
        TextField("snippet"),
        VectorField("embedding", 
                "FLAT", {
                    "TYPE": "FLOAT32",
                    "DIM": 384,
                    "DISTANCE_METRIC": "COSINE"
                })
    )

    definition = IndexDefinition(
        prefix=['emails:'],
        index_type=IndexType.HASH,
    )

    r.ft(REDIS_EMAIL_INDEX).create_index(schema, definition=definition)
```

## Tích hợp với AI model

Chúng ta sẽ viết một hàm giúp mô hình AI __truy vấn dữ liệu__ trong RediSearch. Hàm này sẽ tìm và trả về __k email phù hợp nhất__ với truy vấn đầu vào.

```python
def search_redis(query, k=5):
    r = get_redis(0)
    query_embedding = embed_text(query)

    q = (
        Query("*=>[KNN $K @embedding $BLOB AS score]")
        .return_fields("id", "subject", "sender", "date", "snippet", "body", "score")
        .dialect(2)
    )
    
    query_params = {
        "K": k,
        "BLOB": query_embedding,
    }

    results = r.ft(REDIS_EMAIL_INDEX).search(q, query_params)
    
    if not results.docs:
        return []
    
    # Format results
    emails = []
    for doc in results.docs:
        email_data = {
            'id': doc.id.replace(REDIS_EMAIL_PREFIX_KEY, ''),
            'subject': doc.subject,
            'sender': doc.sender,
            'date': doc.date,
            'snippet': doc.snippet,
            'body': doc.body,
            'score': doc.score
        }
        emails.append(email_data)
        
    return emails
```


Chúng ta sẽ sử dụng mô hình AI thông qua [Ollama SDK cho Python](https://github.com/ollama/ollama-python).

Khi nhận được truy vấn, bước đầu tiên là hỏi AI xem có cần tìm kiếm thông tin trong database trước hay không.
-	Nếu cần, hệ thống sẽ truy vấn dữ liệu từ database và thêm vào context để AI phân tích, từ đó đưa ra kết quả chính xác hơn.
-	Nếu không, truy vấn sẽ được gửi trực tiếp đến mô hình AI để xử lý ngay.

```python
try:
    query = input("Me: ")

    rich_query = f'''
    This is my query: {query}
    You can use function search_redis to search emails in redis database performantly.
    Do you want to use this function?
    Must responds only with yes or no.
    '''

    response = generate(
        model="llama3.1:8b",
        prompt=rich_query,
    )

    print('BOT: Hmm, Should I search the database? ', response.response)

    if response.response == "yes":
        results = search_redis(query, 2)
        context = '\n\n'.join([
            f'''
            Subject: {email['subject']}
            Snippet: {email['snippet']}
            From: {email['sender']}
            Date: {email['date']}
            '''
            for email in results
        ])

        query_with_context = f'''
        This is my query: {query}
        This is the context: {context} 
        Please use the results base on context
        '''

        print('AI: ', end='')
        for chunk in generate(
            model="llama3.1:8b",
            prompt=query_with_context,
            stream=True
        ):
            print(chunk.response, end='', flush=True)
        print('')

    else:
        print('AI: ', end='')
        for chunk in generate(
            model="llama3.1:8b",
            prompt=query,
            stream=True
        ):
            if 'response' in chunk:
                print(chunk['response'], end='', flush=True)
        print('')
        
except KeyboardInterrupt:
    exit(0)
```

## Demo

<div style={{ witdth: '100%', display: 'flex', justifyContent: 'center' }}><iframe width="560" height="315" style={{maxWidth: "100%"}} src="https://www.youtube.com/embed/KSenNT42C-Q?si=PwOjFPo6Q7TWNtuX" title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerPolicy="strict-origin-when-cross-origin" allowFullScreen></iframe></div>

## What's next?

Cách tích hợp AI với vector search như trên tuy đơn giản nhưng chưa thực sự hiệu quả và khó mở rộng. Vì vậy, trong bài viết tiếp theo, mình sẽ giới thiệu một phương pháp tích hợp chuẩn hóa, đang dần trở thành tiêu chuẩn trong cộng đồng AI: Model Context Protocol (MCP).

MCP hiện đã được áp dụng trong một số sản phẩm AI như Claude Desktop và Cursor AI Editor. Hãy cùng khám phá phương pháp này trong bài viết tiếp theo!

Hẹn gặp lại! 🚀

## Đọc thêm

Nếu các bạn có hứng thú với việc cài đặt một hệ thống RAG thuần tuý bằng code Python mà không sử dụng RediSearch, bạn có thể tham khảo ở đây [llama2 demo](https://github.com/magiskboy/llma2-demo)