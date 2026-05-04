---
name: grpc-patterns
description: Implements gRPC development patterns including protocol buffer definitions, unary/streaming RPCs, error handling, and debugging techniques for cloud-native microservices
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  role: implementation
  scope: implementation
  output-format: code
  triggers: grpc development, grpc debugging, protocol buffers, rpc services, grpc errors, stream handling, unary calls, grpc gateway
  related-skills: coding-fastapi-patterns, coding-rest-api-patterns, agent-docker-debugging

---

# gRPC Development Patterns

Implements comprehensive gRPC development patterns for cloud-native microservices including protocol buffer definitions, unary and streaming RPC patterns, error handling with status codes, gRPC Gateway integration, authentication mechanisms, and debugging techniques.

## TL;DR Checklist

- [ ] Define `.proto` files with syntax "proto3", proper package names, and clear service definitions
- [ ] Choose RPC type: unary for request-response, client-streaming for upload, server-streaming for subscriptions, bidirectional for chat
- [ ] Use `google.protobuf.Timestamp` and `google.protobuf.Duration` for time values instead of custom fields
- [ ] Always include `google.api.http` annotations for REST-JSON compatibility via gRPC Gateway
- [ ] Implement proper error handling with `grpc_status` codes (NOT HTTP status codes)
- [ ] Add authentication middleware (JWT, mTLS, API keys) at the gRPC interceptor level
- [ ] Enable TLS in production with proper certificate chains
- [ ] Debug with `grpc_cli` or `grpcurl` to test services without client code

---

## When to Use

Use gRPC when:

- Building high-performance microservices with low-latency, high-throughput requirements
- Implementing real-time streaming APIs (server-streaming for notifications, bidirectional for chat)
- You need strong typing with Protocol Buffers for multi-language service contracts
- Building internal service-to-service communication with predictable, structured data
- You require client-side load balancing and connection pooling out of the box
- When you need bidirectional streaming for collaborative applications or live updates

---

## When NOT to Use

Avoid gRPC for:

- Public-facing APIs consumed by web browsers directly (use REST/gRPC Gateway with CORS)
- Simple CRUD operations where HTTP caching matters (use REST with proper cache headers)
- Environments without Protocol Buffer compiler tooling available
- When you need human-readable request bodies in logs (Protobuf is binary)
- Legacy systems that only support JSON-over-HTTP
- Scenarios requiring partial responses or flexible schemas (Protobuf requires schema evolution planning)

---

## Core Workflow

1. **Define Protocol Buffer Schema** — Create `.proto` files with message types and service definitions. **Checkpoint:** All messages have unique field numbers (1-536,870,911) and proper syntax declaration.

2. **Choose RPC Pattern** — Select unary, client-streaming, server-streaming, or bidirectional based on data flow needs. **Checkpoint:** Document the streaming pattern choice with use case justification.

3. **Generate Code** — Run `protoc` compiler with language-specific plugins (Go, Python, TypeScript). **Checkpoint:** Generated files compile without errors and match service contract.

4. **Implement Server Logic** — Write handler functions for each RPC method with proper error handling. **Checkpoint:** All error paths return appropriate `grpc_status` codes.

5. **Add Middleware** — Implement interceptors for authentication, logging, and metrics. **Checkpoint:** Middleware chain processes requests before handlers.

6. **Debug and Test** — Use `grpc_cli` or `grpcurl` to test services, then write unit/integration tests with mock servers. **Checkpoint:** Test coverage includes both success and error status code scenarios.

---

## Implementation Patterns

### Pattern 1: Protocol Buffer Definition Structure

**Description:** Proper `.proto` file organization with package names, imports, and message definitions following Google's API design guidelines.

```protobuf
syntax = "proto3";

package acme.user.v1;

import "google/protobuf/timestamp.proto";
import "google/api/annotations.proto";

// User represents a registered user in the system
message User {
  // Unique identifier for the user
  string user_id = 1;
  
  // User's full name
  string name = 2;
  
  // User's email address (must be unique)
  string email = 3;
  
  // Account creation timestamp
  google.protobuf.Timestamp created_at = 4;
}

// GetUserRequest is the request message for GetUser RPC
message GetUserRequest {
  // The unique identifier of the user to retrieve
  string user_id = 1 [(google.api.field_behavior) = REQUIRED];
}

// UserService provides user management operations
service UserService {
  // GetUser retrieves a user by their unique identifier
  rpc GetUser(GetUserRequest) returns (User) {
    option (google.api.http) = {
      get: "/v1/users/{user_id}"
    };
  }
}
```

### Pattern 2: Unary RPC Pattern

**Description:** Simple request-response pattern for traditional API operations. Best for operations that complete quickly and return a single response.

```protobuf
message SearchUsersRequest {
  // Search query string
  string query = 1;
  
  // Maximum number of results to return
  int32 limit = 2 [(google.api.field_behavior) = OPTIONAL];
  
  // Pagination token for next page
  string page_token = 3;
}

message SearchUsersResponse {
  // List of matching users
  repeated User users = 1;
  
  // Token for fetching next page, empty if no more results
  string next_page_token = 2;
  
  // Total count of matching users
  int32 total_size = 3;
}
```

### Pattern 3: Client-Streaming RPC Pattern

**Description:** Client sends a stream of messages to the server, which returns a single response after receiving all messages. Perfect for file uploads or batch processing.

```protobuf
message UploadRequest {
  oneof payload {
    UploadMetadata metadata = 1;
    bytes data = 2;
  }
}

message UploadMetadata {
  string filename = 1;
  string content_type = 2;
  int64 total_size = 3;
}

message UploadResponse {
  // Unique identifier for uploaded file
  string file_id = 1;
  
  // Total bytes received
  int64 bytes_received = 2;
  
  // Upload completion timestamp
  google.protobuf.Timestamp completed_at = 3;
}

service FileService {
  // UploadFile accepts a stream of file chunks from the client
  rpc UploadFile(stream UploadRequest) returns (UploadResponse) {
    option (google.api.http) = {
      post: "/v1/files/upload"
      body: "*"
    };
  }
}
```

### Pattern 4: Server-Streaming RPC Pattern

**Description:** Server sends a stream of responses to the client after receiving a single request. Ideal for subscriptions, live updates, or large result sets.

```protobuf
message SubscribeToNotificationsRequest {
  // User ID to subscribe to notifications for
  string user_id = 1 [(google.api.field_behavior) = REQUIRED];
  
  // Optional filter for notification types
  repeated string types = 2;
}

message Notification {
  // Unique notification identifier
  string notification_id = 1;
  
  // Notification content
  string message = 2;
  
  // Notification type (e.g., "alert", "update", "warning")
  string type = 3;
  
  google.protobuf.Timestamp timestamp = 4;
}

service NotificationService {
  // SubscribeToNotifications sends a stream of notifications to the client
  rpc SubscribeToNotifications(SubscribeToNotificationsRequest) returns (stream Notification) {
    option (google.api.http) = {
      get: "/v1/notifications/subscribe"
    };
  }
  
  // GetNotificationHistory returns historical notifications with pagination
  rpc GetNotificationHistory(NotificationHistoryRequest) returns (stream Notification) {
    option (google.api.http) = {
      get: "/v1/users/{user_id}/notifications/history"
    };
  }
}
```

### Pattern 5: Bidirectional Streaming RPC Pattern

**Description:** Both client and server send streams of messages. Perfect for real-time chat, collaborative editing, or interactive games.

```protobuf
message ChatMessage {
  // Unique message identifier
  string message_id = 1;
  
  // Message content
  string text = 2;
  
  // Message sender
  string sender_id = 3;
  
  // Optional message timestamp (server sets if omitted)
  google.protobuf.Timestamp timestamp = 4;
  
  // Message sequence number for ordering
  int64 sequence_number = 5;
  
  // Optional parent message ID for threading
  string parent_message_id = 6;
}

message ChatStreamControl {
  // Request client to pause/resume streaming
  enum FlowControl {
    FLOW_UNSET = 0;
    FLOW_PAUSE = 1;
    FLOW_RESUME = 2;
  }
  
  FlowControl action = 1;
  int32 buffer_size = 2;
}

service ChatService {
  // Chat allows bidirectional real-time messaging
  rpc Chat(stream ChatMessage) returns (stream ChatMessage) {
    option (google.api.http) = {
      post: "/v1/chats/{chat_id}/stream"
      body: "*"
    };
  }
  
  // StreamChatStatus receives control messages for flow control
  rpc StreamChatStatus(stream ChatStreamControl) returns (stream ChatStreamControl);
}
```

### Pattern 6: Error Handling with gRPC Status Codes

**Description:** Proper error handling using `grpc_status` codes instead of HTTP status codes. Always include descriptive error messages and metadata.

```protobuf
import "google/rpc/error_details.proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (User) {
    // Server implementation returns appropriate status codes
  }
  
  rpc CreateUser(CreateUserRequest) returns (User) {
    // Returns ALREADY_EXISTS when email already registered
  }
}

// Error response structure for client consumption
message ErrorInfo {
  // The reason code for the error
  string reason = 1;
  
  // The domain where the error occurred
  string domain = 2;
  
  // Additional error details as key-value pairs
  map<string, string> metadata = 3;
}
```

**Go server implementation:**

```go
import (
  "google.golang.org/grpc/codes"
  "google.golang.org/grpc/status"
  "google.golang.org/genproto/googleapis/rpc/errdetails"
)

func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
  user, err := s.db.GetUser(req.UserId)
  if err != nil {
    if errors.Is(err, database.ErrNotFound) {
      return nil, status.Error(codes.NotFound, "user not found")
    }
    return nil, status.Error(codes.Internal, "database error")
  }
  return user, nil
}
```

### Pattern 7: gRPC Gateway for REST-JSON Compatibility

**Description:** Use `grpc-gateway` to expose gRPC services via REST-JSON endpoints. This allows web browsers and HTTP-only clients to consume your gRPC services.

```protobuf
syntax = "proto3";

package acme.api.v1;

import "google/api/annotations.proto";
import "google/api/client.proto";
import "google/api/field_behavior.proto";

service UserService {
  option (google.api.http) = {
    get: "/v1/users/{user_id}"
    additional_bindings: {
      get: "/v1/users"
      body: ""
    }
  };
  
  // GetUser retrieves a user by ID
  rpc GetUser(GetUserRequest) returns (User) {
    option (google.api.http) = {
      get: "/v1/users/{user_id}"
    };
  }
  
  // ListUsers retrieves paginated users
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {
    option (google.api.http) = {
      get: "/v1/users"
    };
  }
  
  // CreateUser creates a new user
  rpc CreateUser(CreateUserRequest) returns (User) {
    option (google.api.http) = {
      post: "/v1/users"
      body: "user"
    };
  }
}
```

**Go server setup for gRPC Gateway:**

```go
package main

import (
	"context"
	"flag"
	"net/http"
	
	"github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
	"google.golang.org/grpc"
	
	pb "path/to/your/generated/proto"
)

var (
	grpcServerAddr = flag.String("grpc-server", "localhost:9090", "gRPC server address")
	grpcGatewayAddr = flag.String("http-server", "localhost:8080", "HTTP gateway address")
)

func main() {
	flag.Parse()
	
	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()
	
	mux := runtime.NewServeMux()
	opts := []grpc.DialOption{
		grpc.WithInsecure(),
		grpc.WithDefaultCallOptions(grpc.MaxCallRecvMsgSize(1024*1024*16)),
	}
	
	err := pb.RegisterUserServiceHandler(ctx, mux, *grpcServerAddr, opts)
	if err != nil {
		panic(err)
	}
	
	http.ListenAndServe(*grpcGatewayAddr, mux)
}
```

**Testing with curl:**

```bash
curl -X GET "http://localhost:8080/v1/users/123"
curl -X POST "http://localhost:8080/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### Pattern 8: Authentication and Authorization Middleware

**Description:** Implement authentication at the gRPC interceptor level using JWT tokens.

```go
package auth

import (
	"context"
	"strings"
	
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

const AuthMetadataKey = "authorization"

func ExtractToken(ctx context.Context) (string, error) {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return "", status.Error(codes.Unauthenticated, "no metadata")
	}
	
	authHeader := md.Get(AuthMetadataKey)
	if len(authHeader) == 0 {
		return "", status.Error(codes.Unauthenticated, "missing authorization header")
	}
	
	parts := strings.Split(authHeader[0], " ")
	if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
		return "", status.Error(codes.Unauthenticated, "invalid authorization format")
	}
	
	return parts[1], nil
}

type JWTClaims struct {
	UserID   string `json:"user_id"`
	Role     string `json:"role"`
	Email    string `json:"email"`
	Expires  int64  `json:"exp"`
}

func ServerAuthInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		if isPublicEndpoint(info.FullMethod) {
			return handler(ctx, req)
		}
		
		token, err := ExtractToken(ctx)
		if err != nil {
			return nil, err
		}
		
		claims, err := validateJWT(token)
		if err != nil {
			return nil, status.Error(codes.Unauthenticated, "invalid token")
		}
		
		newCtx := context.WithValue(ctx, "claims", claims)
		return handler(newCtx, req)
	}
}

func isPublicEndpoint(method string) bool {
	publicMethods := map[string]bool{
		"/acme.api.v1.UserService/Login":    true,
		"/acme.api.v1.UserService/Register": true,
		"/grpc.health.v1.Health/Check":      true,
	}
	return publicMethods[method]
}

func validateJWT(tokenString string) (*JWTClaims, error) {
	claims := &JWTClaims{
		UserID: "user123",
		Role:   "user",
		Email:  "user@example.com",
		Expires: time.Now().Add(time.Hour).Unix(),
	}
	return claims, nil
}
```

### Pattern 9: Protocol Buffer Best Practices

**Description:** Follow Google's API design guidelines for consistent, maintainable protobuf definitions.

```protobuf
syntax = "proto3";

package acme.user.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/duration.proto";
import "google/api/field_behavior.proto";

message UserProfile {
  // User's first name (required, 1-50 characters)
  string first_name = 1 [(google.api.field_behavior) = REQUIRED];
  
  // User's last name (required, 1-50 characters)
  string last_name = 2 [(google.api.field_behavior) = REQUIRED];
  
  // User's age in years (non-negative)
  uint32 age = 3;
  
  // Whether the user account is active
  bool is_active = 4;
  
  // Timestamp when the profile was created
  google.protobuf.Timestamp created_at = 5;
  
  // Optional timezone offset in seconds from UTC
  int32 timezone_offset = 6;
}
```

### Pattern 10: Protocol Buffer File Organization

**Description:** Organize large projects with proper file structure and package naming.

```
proto/
├── acme/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── user_service.proto
│   │   │   ├── order_service.proto
│   │   │   └── common.proto
│   │   └── v2/
│   │       └── user_service.proto
│   └── internal/
│       └── admin.proto
└── third_party/
    ├── google/
    │   └── api/
    │       └── annotations.proto
```

---

## Debugging Techniques

### Using grpc_cli for Testing

**Install grpc_cli:**

```bash
git clone https://github.com/grpc/grpc.git
cd grpc
make
sudo make install
```

**Basic grpc_cli Usage:**

```bash
# List available services
grpc_cli ls localhost:9090

# List methods in a service
grpc_cli ls localhost:9090 acme.user.v1.UserService

# Get service information
grpc_cli call localhost:9090 'acme.user.v1.UserService.GetUser' 'user_id: "123"'

# With TLS
grpc_cli call localhost:9090 'acme.user.v1.UserService.GetUser' 'user_id: "123"' \
  --ssl_cacert=/path/to/ca.pem \
  --ssl_key=/path/to/key.pem \
  --ssl_cert=/path/to/cert.pem
```

### Using grpcurl (simpler alternative)

```bash
# List services
grpcurl -plaintext localhost:9090 list

# List methods in a service
grpcurl -plaintext localhost:9090 list acme.user.v1.UserService

# Call a unary method
grpcurl -plaintext -d '{"user_id": "123"}' localhost:9090 acme.user.v1.UserService.GetUser

# Call with custom metadata
grpcurl -plaintext -H 'authorization: Bearer mytoken' -d '{"user_id": "123"}' localhost:9090 acme.user.v1.UserService.GetUser

# With TLS
grpcurl -cert client.crt -key client.key -ca-cert server.crt localhost:9090 list
```

### Go Debugging with Verbose Logging

```go
package main

import (
	"fmt"
	"os"
	
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/grpclog"
)

func main() {
	grpclog.SetLoggerV2(grpclog.NewLoggerV2(os.Stdout, os.Stdout, os.Stdout))
	
	conn, err := grpc.Dial("localhost:9090",
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithDefaultCallOptions(
			grpc.MaxCallRecvMsgSize(1024*1024*16),
		),
	)
	if err != nil {
		panic(err)
	}
	defer conn.Close()
	
	fmt.Println("gRPC connection established")
}
```

### Python Debugging

```python
import os
import grpc

os.environ['GRPC_VERBOSITY'] = 'DEBUG'
os.environ['GRPC_TRACE'] = 'all'

channel = grpc.insecure_channel('localhost:9090', options=[
    ('grpc.max_receive_message_length', 16 * 1024 * 1024),
])
```

---

## Performance Optimization

### Connection Pooling

```go
package pool

import (
	"context"
	"sync"
	"time"
	
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type ClientPool struct {
	target   string
	pool     []*grpc.ClientConn
	mu       sync.Mutex
	maxSize  int
	current  int
}

func NewClientPool(target string, maxSize int) *ClientPool {
	return &ClientPool{
		target:   target,
		maxSize:  maxSize,
		pool:     make([]*grpc.ClientConn, 0, maxSize),
		current:  0,
	}
}

func (p *ClientPool) GetConnection(ctx context.Context) (*grpc.ClientConn, error) {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	for i, conn := range p.pool {
		if conn != nil && conn.GetState() == grpc.Ready {
			p.pool[i] = nil
			return conn, nil
		}
	}
	
	if p.current < p.maxSize {
		conn, err := grpc.DialContext(ctx, p.target,
			grpc.WithTransportCredentials(insecure.NewCredentials()),
			grpc.WithDefaultCallOptions(
				grpc.MaxCallRecvMsgSize(16*1024*1024),
			),
		)
		if err != nil {
			return nil, err
		}
		p.current++
		return conn, nil
	}
	
	return nil, grpc.ErrClientConnTimeout
}
```

### Streaming Optimization

```go
package stream

import (
	"context"
	"io"
	
	"google.golang.org/grpc"
	"google.golang.org/grpc/encoding/gzip"
)

func SendCompressedStream(ctx context.Context, conn *grpc.ClientConn) error {
	stream, err := conn.NewStream(
		ctx,
		&grpc.StreamDesc{
			ServerStreams: true,
			ClientStreams: true,
		},
		"/acme.api.v1.StreamService/CompressedStream",
		grpc.UseCompressor(gzip.Name),
	)
	if err != nil {
		return err
	}
	
	for i := 0; i < 1000; i++ {
		msg := make([]byte, 10000)
		if err := stream.SendMsg(msg); err != nil {
			return err
		}
	}
	
	return stream.CloseSend()
}
```

### Batch Processing

```go
package batch

import (
	"context"
	"sync"
	"time"
	
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type BatchProcessor struct {
	conn      *grpc.ClientConn
	client    pb.BatchServiceClient
	batchSize int
	timeout   time.Duration
}

func NewBatchProcessor(target string, batchSize int, timeout time.Duration) (*BatchProcessor, error) {
	conn, err := grpc.Dial(target,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, err
	}
	
	return &BatchProcessor{
		conn:      conn,
		client:    pb.NewBatchServiceClient(conn),
		batchSize: batchSize,
		timeout:   timeout,
	}, nil
}

func (p *BatchProcessor) ProcessBatch(ctx context.Context, items []pb.Item) error {
	for i := 0; i < len(items); i += p.batchSize {
		end := i + p.batchSize
		if end > len(items) {
			end = len(items)
		}
		
		batch := items[i:end]
		batchCtx, cancel := context.WithTimeout(ctx, p.timeout)
		defer cancel()
		
		_, err := p.client.ProcessBatch(batchCtx, &pb.BatchRequest{
			Items: batch,
		})
		if err != nil {
			return err
		}
	}
	
	return nil
}
```

---

## Constraints

### MUST DO

- Always define `syntax = "proto3"` at the top of each `.proto` file
- Use `google.protobuf.Timestamp` for timestamps, never custom time fields
- Implement proper error handling with `grpc_status` codes, not HTTP status codes
- Add `google.api.http` annotations for gRPC Gateway compatibility
- Use `google.api.field_behavior` annotations to mark required/optional fields
- Enable TLS in production environments
- Implement authentication via gRPC interceptors, not in handler methods
- Set appropriate timeouts for all gRPC calls
- Use connection pooling for high-throughput client applications
- Always include request IDs in metadata for distributed tracing

### MUST NOT DO

- Never use `required` in proto3 (it's deprecated and unsupported)
- Never mix HTTP status codes with gRPC status codes
- Never disable TLS in production
- Never handle authentication in individual handler methods (use interceptors)
- Never send unbounded streams without cancellation support
- Never ignore context cancellation in streaming methods
- Never use magic numbers for field tags (always use consecutive numbering)
- Never include sensitive data in error messages sent to clients

---

## Output Template

When this skill is active, your output must include:

1. **Protocol Buffer Definitions** — Complete `.proto` file syntax with proper package names, imports, message types, and service definitions

2. **RPC Pattern Selection** — Clear explanation of why a particular RPC pattern (unary, client-streaming, server-streaming, bidirectional) was chosen for the use case

3. **Error Handling** — Complete error handling implementation using `grpc_status` codes with appropriate status messages

4. **Interceptor Implementation** — Go/Python interceptors for authentication, logging, and metrics if applicable

5. **Debugging Commands** — `grpc_cli` or `grpcurl` commands for testing the service

6. **Performance Considerations** — Connection pooling, compression, and batch processing recommendations based on the use case

---

## Related Skills

| Skill | Purpose |
|---|---|
| `coding-fastapi-patterns` | REST API patterns with FastAPI; use alongside gRPC for hybrid architectures where external APIs need REST while internal services use gRPC |
| `coding-rest-api-patterns` | RESTful API design patterns; helpful when designing gRPC Gateway endpoints for web browser compatibility |
| `agent-docker-debugging` | Docker and container debugging; use for deploying and debugging gRPC services in containerized environments |

---

## References

- [gRPC Documentation](https://grpc.io/docs/) — Official gRPC documentation and guides
- [Protocol Buffers Language Guide](https://developers.google.com/protocol-buffers/docs/proto3) — Complete protobuf syntax reference
- [gRPC Gateway](https://github.com/grpc-ecosystem/grpc-gateway) — gRPC to REST proxy
- [gRPC Status Codes](https://grpc.github.io/grpc/core/md_doc_statuscodes.html) — Complete list of gRPC status codes
- [Google API Design Guide](https://google.aip.dev/) — Best practices for API design including gRPC

---

> 📖 skill: grpc-patterns
