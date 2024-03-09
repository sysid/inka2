# Java Testing, JUnit5
File tests duplicate occurrence of question string in file.

# Mocking ..........................................................................................
## Explain mockito `Spy`:

---
<!--ID:1709993468182-->
1. Explain mockito `Spy`:
> is an object to wrap a real instance of a class and track its interactions, while still maintaining the behavior of the real object.

---

```java
// Prepare a mocked CompletionService
CompletionService<Void> mockedWbTwinExceptionHandlingExecutor = Mockito.mock(CompletionService.class);
when(mockedWbTwinExceptionHandlingExecutor.take()).thenReturn(future);
```
You don't have to use the Mockito extension for JUnit, but with the extension included in your dependencies mocking becomes much easier to do.
The extension allows you for example, to use @Mock and @InjectMock.

